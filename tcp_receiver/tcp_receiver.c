#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/wait.h>

#define MAX_LINE 4096
#define BUFFSIZE 4096
#define PORT htons(55555)


void writefile(int listen_socket, FILE *fp);
ssize_t total=0;
void HandleConnection(int sock);


int main(void)
{
    
    int listen_socket, client_socket;
    struct sockaddr_in adr;
    socklen_t dladr = sizeof(struct sockaddr_in);
    
    listen_socket = socket(PF_INET, SOCK_STREAM, 0);
    if (listen_socket == -1) 
    {
        perror("Unable to allocate listen_socket");
        exit(1);
    }
    else printf("listen_socket allocated\n");

    adr.sin_family = AF_INET;
    adr.sin_port = PORT;
    adr.sin_addr.s_addr = INADDR_ANY;
    memset(adr.sin_zero, 0, sizeof(adr.sin_zero));
    
    if (bind(listen_socket, (struct sockaddr*) &adr, dladr) < 0)
    {
        printf("Main: bind failed\n");
        exit(1);
    }
    else printf("Main: bind ok\n");
    
    listen(listen_socket, 10);
    
    while(1)
    {
    	printf("\n------------------------------\n");
        dladr = sizeof(struct sockaddr_in);
        client_socket = accept(listen_socket, (struct sockaddr*) &adr, &dladr);
        if (client_socket < 0)
        {
            perror("Main: accept returned error\n");
	    sleep(1);
            exit(1);
        }
	else printf("Main: accept ok\n");
        printf("Main: connection from %s:%u\n", 
            inet_ntoa(adr.sin_addr),
            ntohs(adr.sin_port)
            );
        printf("Main: creating child process\n");
	// zombie fix -> double fork
	pid_t pid1;
     	pid_t pid2;
     	int status;
	if(pid1 = fork())
	{	
		/* parent process A */
		waitpid(pid1, &status, NULL);
	}
	else if(!pid1)
	{
		/* child process B */
		if(pid2 = fork())
		{
			exit(0);
		}
		else if(!pid2)
		{
			/* child process C */
			/* child process */
            		printf("Child: starting handling\n");
            		HandleConnection(client_socket);
            		printf("Child: closing socket\n");
	    		usleep(20000);
	    		shutdown(client_socket, 2);
            		close(client_socket);
            		printf("Child: ending process\n");
            		exit(0);
		}
		else
		{
			/*error*/
		}
	}
        else
        {
		/*error*/
		/* parent process */
		printf("Main: back to listen\n");
		continue;
        }
    }
    return 0;
}


void HandleConnection(int sock)
{
    char filename[BUFFSIZE] = {0}; 
    if (recv(sock, filename, BUFFSIZE, 0) == -1) 
    {
        perror("Child: Unable to read filename");
        exit(1);
    }
    else printf("Child: Filename received\n");

    // accepting only name starting with letter
    if((filename[0] >= 97 && filename[0] <= 122) || (filename[0] >= 65 && filename[0] <= 90))
    { 
        int size = sizeof filename / sizeof filename[0];
        printf("size: %u\n", size);
        for(int i=1; i<size; i++)
        {
            if (filename[i] != 0)
            {
                
                if((filename[i] >= 0 && filename[i] <= 45) || (filename[i] == 47) || (filename[i] >= 58 && filename[i] <= 64) || (filename[i] >= 91 && filename[i] <= 94) || (filename[i] == 96) || (filename[i] >= 123 && filename[i] <= 255))
                {
                    printf("Child: Achtung: %c\n", filename[i]);
                    perror("Child: Filename contains unacceptable character! Rejecting... ");
                    exit(1);    
                }
            }
        }
        printf("Child: Value of filename: %s\n", filename);
        printf("Child: Filename acceptable. Processing... \n");
    }
    else
    {
        perror("Child: Filename not starting with letter! Rejecting... ");
        exit(1);
    }

    char buf[0x100];
    sprintf(buf, "/home/qrv/tcp_receiver/received/%s", filename); 
    printf("%s", buf+'\n');
    
    FILE *fp = fopen(/*filename*/buf, "wb"); //
    if (fp == NULL) 
    {
        perror("Child: Unable to open file");
	exit(1);
    }
    else printf("\nChild: File opened\n");
    
    char addr[INET_ADDRSTRLEN];
    printf("Child: Starting receiving the file: %s\n", /*filename*/buf);
    writefile(sock, fp); 
    printf("Child: Receiving done, received %ld bytes\n", total);
    fclose(fp);

}


void writefile(int listen_socket, FILE *fp)
{
    ssize_t n;
    char buff[MAX_LINE] = {0};
    while ((n = recv(listen_socket, buff, MAX_LINE, 0)) > 0) 
    {
	    total+=n;
        if(total > 4096*9)
        {
            perror("Child: File to large! Stopping transfer!");
            exit(1);
        }
        if (n == -1)
        {
            perror("Child: Error while receiving file");
            exit(1);
        }
	else printf("Child: Receiving...  ");
        
        if (fwrite(buff, sizeof(char), n, fp) != n)
        {
            perror("Child: Error writing to file");
            exit(1);
        }
	else printf("Child: Saving...\n");
        memset(buff, 0, MAX_LINE);
    }
}


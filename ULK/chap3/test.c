#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <stdlib.h>
#include <sys/syscall.h>

int main(int argc, char **argv)
{
    if (argc != 2 ) {
        printf("Usage: %s syscall_nr\n", argv[0]);
        return -1;
    }
    long nr = strtol(argv[1], NULL, 10);
    if (syscall(nr) < 0) {
        perror("syscall");
        return -1;
    }

    return 0;
}
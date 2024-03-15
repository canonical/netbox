#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
   if (argc < 2) {
     fprintf(stderr, "Usage is: %s [ARGUMENTS]...\n", argv[0]);
     _exit(EXIT_FAILURE);
   }

   sleep(1);
   int rc = execvp(argv[1], &argv[1]);
   if (rc == -1) {
     perror("execvp failed");
   }
   _exit(EXIT_FAILURE);
}

#include <stdio.h>
#include <stdlib.h>

int main() {
    const char *file_name = "gpssim.bin";
    FILE *file;

    file = fopen(file_name, "rb");
    if (file == NULL) {
        perror("Error opening file");
        return 1;
    }

    int c;
    while ((c = fgetc(file)) != EOF) {
        for (int i = 7; i >= 0; i--) {
            if (c & (1 << i)) {
                putchar('1');
            } else {
                putchar('0');
            }
        }
    }

    fclose(file);

    return 0;
}


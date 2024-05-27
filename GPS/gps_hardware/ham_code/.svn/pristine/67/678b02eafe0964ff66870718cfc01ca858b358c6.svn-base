#include <stdio.h>
#include <stdlib.h>

void convertToLittleEndian(const unsigned char *data, int dataLength, unsigned char *result)
{
    int total_bits = dataLength * 8;
    unsigned char output_byte = 0;
    int output_bit_position = 7;
    int result_index = 0;

    for (int i = 0; i < total_bits; i++) {
        unsigned char bit = (data[i / 8] >> (i % 8)) & 1;
        output_byte |= (bit << output_bit_position);
        output_bit_position--;
        if (output_bit_position < 0) {
            result[result_index] = output_byte;
            output_byte = 0;
            output_bit_position = 7;
            result_index++;
        }
    }
}

int main() 
{
    const char *inputFile = "gpssim.bin"; 
    FILE *file = fopen(inputFile, "rb");
    const int fc = 1000000;
    const int fs = 2048000;


    if (!file) 
    {
        perror("File open error");
        return 1;
    }
    fseek(file, 0, SEEK_END);
    long fileSize = ftell(file);
    fseek(file, 0, SEEK_SET);
    unsigned char *data = (unsigned char *)malloc(fileSize);
    unsigned char *data_buff = (unsigned char *)malloc(fileSize/2);

    if (!data)
    {
        perror("Memory allocation error");
        fclose(file);
        return 1;
    }
    if (!data_buff) 
    {
        perror("Memory allocation error");
        fclose(file);
        return 1;
    }

    size_t bytesRead = fread(data, 1, fileSize, file);

    if (bytesRead != fileSize) 
    {
        perror("File read error");
        free(data);
        fclose(file);
        return 1;
    }

    fclose(file);

    unsigned char *even = (unsigned char *)malloc(fileSize * 4);
    unsigned char *odd = (unsigned char *)malloc(fileSize * 4);
    unsigned char *sum = (unsigned char *)malloc(fileSize * 4);
    unsigned char *I = (unsigned char *)malloc(fileSize * 4);
    unsigned char *Q = (unsigned char *)malloc(fileSize * 4);
    unsigned char *result = (unsigned char *)malloc(fileSize/2);

    if (!even) 
    {
        perror("Memory allocation error");
        free(data);
        return 1;
    }

    if (!odd) 
    {
        perror("Memory allocation error");
        free(data);
        return 1;
    }

    if (!sum) 
    {
        perror("Memory allocation error");
        free(data);
        return 1;
    }
    if (!I) 
    {
        perror("Memory allocation error");
        free(data);
        return 1;
    }
    if (!Q) 
    {
        perror("Memory allocation error");
        free(data);
        return 1;
    }

    int x = 0;
    for (int i = 0; i < fileSize; i++) 
    {
        int k = 7;
        for (int j = 7; j >= 0; j -= 2) 
	{
            even[x + (7 - k)] = (data[i] >> j) & 1;
            k--;
        }
        x += 4;
    }


    int v = 0;
    for (int i = 0; i < fileSize; i++) 
    {
        int k = 7;
        for (int j = 7; j >= 0; j -= 2) 
	{
            odd[v + (7 - k)] = (data[i] >> (j-1)) & 1;
            k--;
        }
        v += 4;
    }


    for (int i = 0; i < 8; i++)
    {
        printf("0x%02X ", data[i]);
    }
    printf("\n");

    for (int i = 0; i < 32; i++)
    {
        printf("%d ", even[i]);
    }
    printf("\n");

    printf("\n");
    for (int i = 0; i < 32; i++)
    {
        printf("%d ", odd[i]);
    }
    printf("\n");



    const int lo_sin[4] = {1,1,0,0};
    const int lo_cos[4] = {1,0,0,1};

    double lo_freq = fc;
    double lo_phase = 0;
    double lo_rate = lo_freq/fs*4;


    for(int i=0;i<fileSize*4;i++)
    {
	    I[i]=(even[i] ^ lo_sin[(int)lo_phase]);
	    Q[i]=(odd[i]  ^ lo_cos[(int)lo_phase]);

	    lo_phase += lo_rate;
	    if(lo_phase>=4)
	    {
		    lo_phase -=4;
	    }
    }



    for(int i=0;i<fileSize*4;i++)
    {
	    sum[i]=I[i] | Q[i];
    }


    for (int i = 0; i < 32; i++)
    {
        printf("%d ", sum[i]);
    }
    printf("\n");
    printf("\n");

    for(int i=0;i<fileSize*4;i++)
    {
	    if(i%8 == 0)
	    {
		    data_buff[i/8] = 0x00;
	    }
	    data_buff[i/8] |= (sum[i])<<(7-i%8);
    }




   convertToLittleEndian(data_buff, fileSize/2, result);

    for (int i = 0; i < 128; i++)
    {
        printf("0x%02X ", result[i]);
    }
    printf("\n");

FILE *f = fopen("iq_if.bin", "wb");
    if (!f) 
    {
        perror("File open error");
        return 1;
    }

    // Write the data array to the output binary file
    size_t bytesWritten = fwrite(result, 1, fileSize/2, f);
    if (bytesWritten != fileSize/2) 
    {
        perror("File write error");
        fclose(f);
        return 1;
    }

    // Close the output file
    fclose(f);

    // Don't forget to free the allocated memory
   // unsigned char result[fileSize];
   //convertToLittleEndian(data, fileSize, result);
    free(data);
    free(even);
    free(odd);
    free(I);
    free(Q);
    free(sum);
    free(data_buff);

    return 0;
}


#include <stdio.h>
#include <stdlib.h>
#include <math.h>


void convertToLittleEndian(const unsigned char *data, int dataLength, unsigned char *result)
{
    int total_bits = dataLength * 8;
    unsigned char output_byte = 0;
    int output_bit_position = 7;
    int result_index = 0;

    for (int i = 0; i < total_bits; i++) 
    {
        unsigned char bit = (data[i / 8] >> (i % 8)) & 1;
        output_byte |= (bit << output_bit_position);
        output_bit_position--;
        if (output_bit_position < 0) 
	{
            result[result_index] = output_byte;
            output_byte = 0;
            output_bit_position = 7;
            result_index++;
        }
    }
}

void processDataFile(const char *inputFile, const char *outputFile, int fc, int fs)
{
	
    FILE *inputFilePtr = fopen(inputFile, "rb");
    if (!inputFilePtr) {
        perror("File open error");
        return;
    }

    FILE *outputFilePtr = fopen(outputFile, "wb");
    if (!outputFilePtr) {
        perror("File open error");
        fclose(inputFilePtr);
        return;
    }

    const int buffer_size = 1024; // Adjust based on available memory and performance

    unsigned char *buffer = (unsigned char *)malloc(buffer_size);
    if (!buffer) 
    {
        perror("Memory allocation error");
        fclose(inputFilePtr);
        fclose(outputFilePtr);
        return;
    }

    unsigned char *even = (unsigned char *)malloc(buffer_size * 4);
    unsigned char *odd = (unsigned char *)malloc(buffer_size * 4);
    unsigned char *sum = (unsigned char *)malloc(buffer_size * 4);
    unsigned char *I = (unsigned char  *)malloc(buffer_size * 4);
    unsigned char *Q = (unsigned char *)malloc(buffer_size * 4);
    int *noise_I     = (int *)malloc(buffer_size*4);
    int *noise_Q     = (int *)malloc(buffer_size*4);

    unsigned char *result = (unsigned char *)malloc(buffer_size / 2);
    unsigned char *data_buff = (unsigned char *)malloc(buffer_size / 2);

    if (!even || !odd || !sum || !I || !Q || !result || !noise_I || !noise_Q)
    {
        perror("Memory allocation error");
        fclose(inputFilePtr);
        fclose(outputFilePtr);
        free(buffer);
         free(even);
        free(odd);
        free(sum);
        free(I);
        free(Q);
        free(result);
        free(noise_I);
        free(noise_Q);
        free(data_buff);
        return;
    }

    while (1)
    {
        size_t bytesRead = fread(buffer, 1, buffer_size, inputFilePtr);
        if (bytesRead == 0) 
	{
            break; 
        }

        int x = 0;
        for (size_t i = 0; i < bytesRead; i++)
	{
            int k = 7;
            for (int j = 7; j >= 0; j -= 2) 
	    {
                even[x + (7 - k)] = (buffer[i] >> j) & 1;
                k--;
            }
            x += 4;
        }


    int v = 0;
    for (int i = 0; i < bytesRead; i++)
    {
        int k = 7;
        for (int j = 7; j >= 0; j -= 2) 
	{
            odd[v + (7 - k)] = (buffer[i] >> (j - 1)) & 1;
            k--;
        }
        v += 4;
    }

    const int lo_sin[4] = {1, 1, 0, 0};
    const int lo_cos[4] = {1, 0, 0, 1};
    double lo_freq = fc;
    double lo_phase = 0;
    double lo_rate = lo_freq / fs * 4;

    for (int i = 0; i < bytesRead * 4; i++) 
    {
        I[i] = (even[i] ^ lo_sin[(int)lo_phase]);
        Q[i] = (odd[i] ^ lo_cos[(int)lo_phase]);

        lo_phase += lo_rate;
        if (lo_phase >= 4) 
	{
            lo_phase -= 4;
        }
    }





    for (int i = 0; i < bytesRead * 4; i++)
    {
        sum[i] = I[i] | Q[i];
    }

    for (int i = 0; i < bytesRead * 4; i++)
    {
        if (i % 8 == 0)
	{
            data_buff[i / 8] = 0x00;
        }
        data_buff[i / 8] |= (sum[i]) << (7 - i % 8);
    }

    convertToLittleEndian(data_buff, bytesRead / 2, result);
        size_t bytesWritten = fwrite(result, 1, bytesRead / 2, outputFilePtr);
        if (bytesWritten != bytesRead / 2)
	{
            perror("File write error");
            break;
        }
    }

    // Clean up and close files
    fclose(inputFilePtr);
    fclose(outputFilePtr);
    free(buffer);
    free(even);
    free(odd);
    free(sum);
    free(I);
    free(Q);
    free(result);
    free(noise_I);
        free(noise_Q);
        free(data_buff);
}

int main()
{
    const char *inputFile = "gpssim.bin";
    const char *outputFile = "iq_if.bin";
    const int fs = 2048000;
    const int fc = 1000000;

    processDataFile(inputFile, outputFile, fc, fs);

    return 0;
}


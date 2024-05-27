#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main()
{
	FILE *file;
	FILE *fi;
	FILE *fq;
	file = fopen("gpssim.bin","rb");
	fi = fopen("i.dat","w");
	fq = fopen("q.dat","w");
	int chunk = 2048;
	char *buffer;
	buffer = (char *)malloc(chunk*sizeof(char));

	while(1)
	{
		long bytesRead = fread(buffer,1,2048,file);
		if(bytesRead ==0)
		{
			break;
		}

		for(int i=0;i<bytesRead;i++)
		{
			char sample_I = buffer[2*i];
			fprintf(fi,"%d\n",sample_I);
			char sample_Q = buffer[2*i+1];
			fprintf(fq, "%d\n",sample_Q);
		}
	}

	free(buffer);
	fclose(file);
	fclose(fi);
	fclose(fq);

}




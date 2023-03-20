# -*- coding: utf-8 -*-
def rinex2csv(file, file_header, file_data):
    from datetime import datetime 
    columns = 'GPST,dec_sec,epoch_flag,clock_offset,satId,psr_1,lli_psr_1,ssi_psr_1,phs_1,lli_phs_1,ssi_phs_1,dop_1,lli_dop_1,ssi_dop_1,snr_1,lli_snr_1,ssi_snr_1,psr_2,lli_psr_2,ssi_psr_2,phs_2,lli_phs_2,ssi_phs_2,dop_2,lli_dop_2,ssi_dop_2,snr_2,lli_snr_2,ssi_snr_2,psr_3,lli_psr_3,ssi_psr_3,phs_3,lli_phs_3,ssi_phs_3,dop_3,lli_dop_3,ssi_dop_3,snr_3,lli_snr_3,ssi_snr_3'
    #Header
    header = ''
    with open(file) as hnd:
        for i, line in enumerate(hnd):
            header += line
            if 'END OF HEADER' in line:
                break
            
    f = open(file_header,"w")
    f.write(header)
    f.close()
        
    #Data
    data = ''
    data += columns +'\n'
    with open(file) as hnd:
        for i, line in enumerate(hnd):
            if '> ' in line:
                epoch_flag = line[31]
                if int(epoch_flag) < 2:
                    try:
                        clock_offset = line[40:55]
                    except:
                        clock_offset = ' '
                    year = line[2:6]
                    months = line[7:9]
                    day = line[10:12]
                    hour = line[13:15]
                    minute = line[16:18]
                    second = line[19:29]
                    satNum = line[32:35]
                    time = datetime(int(year),int(months),int(day), int(hour),int(minute),int(float(second)))
                    init_line = time.strftime("%Y-%m-%d %H:%M:%S")+','+ "0." + second[3:] + ',' + epoch_flag + ',' + clock_offset + ','
                    
                    for j in range(1,int(satNum)):
                        satData = hnd.readline()
                        satId = satData[0:3]
                        #first frequency
                        psr_1 = satData[3:17]
                        lli_psr_1 = satData[17]
                        ssi_psr_1 = satData[18]
                        phs_1 = satData[19:33]
                        lli_phs_1 = satData[33]
                        ssi_phs_1 = satData[34]
                        dop_1 = satData[35:49]
                        lli_dop_1 = satData[49]
                        ssi_dop_1 = satData[50]
                        snr_1 = satData[51:65]
                        lli_snr_1 = satData[65]
                        ssi_snr_1 = satData[66]
                        #second frequency
                        try:
                            psr_2 = satData[67:81]
                            lli_psr_2 = satData[81]
                            ssi_psr_2 = satData[82]
                            phs_2 = satData[83:97]
                            lli_phs_2 = satData[97]
                            ssi_phs_2 = satData[98]
                            dop_2 = satData[99:113]
                            lli_dop_2 = satData[113]
                            ssi_dop_2 = satData[114]
                            try:
                                snr_2 = satData[115:129].rstrip('\r\n')
                                try:
                                    lli_snr_2 = satData[129].rstrip('\r\n')
                                    ssi_snr_2 = satData[130].rstrip('\r\n')
                                    try:
                                        # third frequency
                                        psr_3 = satData[131:145]
                                        lli_psr_3 = satData[145]
                                        ssi_psr_3 = satData[146]
                                        phs_3 = satData[147:161]
                                        lli_phs_3 = satData[161]
                                        ssi_phs_3 = satData[162]
                                        dop_3 = satData[163:177]
                                        lli_dop_3 = satData[177]
                                        ssi_dop_3 = satData[178]
                                        snr_3 = satData[179:193]
                                        lli_snr_3 = satData[193]
                                        ssi_snr_3 = satData[194].rstrip('\r\n')
                                    except:
                                        psr_3 = ' '
                                        lli_psr_3 = ' '
                                        ssi_psr_3 = ' '
                                        phs_3 =  ' '
                                        lli_phs_3 = ' '
                                        ssi_phs_3 = ' '
                                        dop_3 =  ' '
                                        lli_dop_3 = ' '
                                        ssi_dop_3 =  ' '
                                        snr_3 = ' '
                                        lli_snr_3 = ' '
                                        ssi_snr_3 = ' '
                                except:
                                    lli_snr_2 = ' '
                                    ssi_snr_2 = ' '
                                    psr_3 = ' '
                                    lli_psr_3 = ' '
                                    ssi_psr_3 = ' '
                                    phs_3 =  ' '
                                    lli_phs_3 = ' '
                                    ssi_phs_3 = ' '
                                    dop_3 =  ' '
                                    lli_dop_3 = ' '
                                    ssi_dop_3 =  ' '
                                    snr_3 = ' '
                                    lli_snr_3 = ' '
                                    ssi_snr_3 = ' '
                            except:
                                snr_2 = ' '
                                lli_snr_2 = ' '
                                ssi_snr_2 = ' '
                                psr_3 = ' '
                                lli_psr_3 = ' '
                                ssi_psr_3 = ' '
                                phs_3 =  ' '
                                lli_phs_3 = ' '
                                ssi_phs_3 = ' '
                                dop_3 =  ' '
                                lli_dop_3 = ' '
                                ssi_dop_3 =  ' '
                                snr_3 = ' '
                                lli_snr_3 = ' '
                                ssi_snr_3 = ' '
                        except:
                            psr_2 = ' '
                            lli_psr_2 = ' '
                            ssi_psr_2 = ' '
                            phs_2 = ' '
                            lli_phs_2 = ' '
                            ssi_phs_2 = ' '
                            dop_2 = ' '
                            lli_dop_2 = ' '
                            ssi_dop_2 = ' '
                            snr_2 = ' '
                            lli_snr_2 = ' '
                            ssi_snr_2 = ' '
                            psr_3 = ' '
                            lli_psr_3 = ' '
                            ssi_psr_3 = ' '
                            phs_3 =  ' '
                            lli_phs_3 = ' '
                            ssi_phs_3 = ' '
                            dop_3 =  ' '
                            lli_dop_3 = ' '
                            ssi_dop_3 =  ' '
                            snr_3 = ' '
                            lli_snr_3 = ' '
                            ssi_snr_3 = ' '
                        
                        f1 = satId + ',' + psr_1 + ',' + lli_psr_1 + ',' + ssi_psr_1 + ',' + phs_1 + ',' + lli_phs_1 + ',' + ssi_phs_1 + ',' + dop_1 + ',' + lli_dop_1 + ',' + ssi_dop_1 + ',' + snr_1 + ',' + lli_snr_1 + ',' + ssi_snr_1 + ','
                        f2 = psr_2 + ',' + lli_psr_2 + ',' + ssi_psr_2 + ',' + phs_2 + ',' + lli_phs_2 + ',' + ssi_phs_2 + ',' + dop_2 + ',' + lli_dop_2 + ',' + ssi_dop_2 + ',' + snr_2 + ',' + lli_snr_2 + ',' + ssi_snr_2 + ','
                        f3 = psr_3 + ',' + lli_psr_3 + ',' + ssi_psr_3 + ',' + phs_3 + ',' + lli_phs_3 + ',' + ssi_phs_3 + ',' + dop_3 + ',' + lli_dop_3 + ',' + ssi_dop_3 + ',' + snr_3 + ',' + lli_snr_3 + ',' + ssi_snr_3

                        data +=  init_line + f1 + f2 + f3 + "\n"

    f = open(file_data,"w")
    f.write(data)
    f.close()
    
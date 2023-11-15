





static void debug_print_orbit(struct Space_vehicle *sv) {
  printf("\nOrbit parameters for SV %i:\n",   sv->id);
  printf("iode      %02X\n",                  sv->nav_orbit.iode);
  printf("double M0        = %2.30g;\n", sv->nav_orbit.mean_motion_at_ephemeris);
  printf("double delta_n   = %2.30g;\n", sv->nav_orbit.delta_n);
  printf("double e         = %2.30g;\n", sv->nav_orbit.e);
  printf("double sqrt_A    = %2.30g;\n", sv->nav_orbit.sqrt_A);
  printf("double omega_0   = %2.30g;\n", sv->nav_orbit.omega_0);
  printf("double i_0       = %2.30g;\n", sv->nav_orbit.inclination_at_ephemeris);
  printf("double w         = %2.30g;\n", sv->nav_orbit.w);
  printf("double omega_dot = %2.30g;\n", sv->nav_orbit.omega_dot);
  printf("double idot      = %2.30g;\n", sv->nav_orbit.idot);
  printf("double Cuc       = %2.30g;\n", sv->nav_orbit.Cuc);
  printf("double Cus       = %2.30g;\n", sv->nav_orbit.Cus);
  printf("double Crc       = %2.30g;\n", sv->nav_orbit.Crc);
  printf("double Crs       = %2.30g;\n", sv->nav_orbit.Crs);
  printf("double Cic       = %2.30g;\n", sv->nav_orbit.Cic);
  printf("double Cis       = %2.30g;\n", sv->nav_orbit.Cis);
  printf("unsigned Toe     = %u;\n", sv->nav_orbit.time_of_ephemeris);
  printf("Fit       %01x\n",                  sv->nav_orbit.fit_flag);
  printf("aodo      %02X\n",                  sv->nav_orbit.aodo);    
  printf("\n");
}

void debug_print_time(struct Space_vehicle *sv) {
  struct tm  ts;
  char       buf[80];
  time_t     timestamp;

  printf("\nTime parameters for SV %i:\n",   sv->id);
  printf("Week No    %i\n", sv->nav_time.week_no);
  printf("Accuracy   %i\n", sv->nav_time.user_range_accuracy);
  printf("Health     %i\n", sv->nav_time.health);
  printf("IDOC       %i\n", sv->nav_time.issue_of_data);
  printf("double T_gd       = %2.30g;\n", sv->nav_time.group_delay);
  printf("double T_oc       = %2.30g;\n", sv->nav_time.reference_time);
  printf("double a_f2       = %2.30g;\n", sv->nav_time.correction_f2);
  printf("double a_f1       = %2.30g;\n", sv->nav_time.correction_f1);
  printf("double a_f0       = %2.30g;\n", sv->nav_time.correction_f0);
  printf("\n");
  
  timestamp = TIME_EPOCH + sv->nav_time.week_no * 604800;
  ts = *localtime(&timestamp);
  strftime(buf, sizeof(buf), "%a %Y-%m-%d %H:%M:%S %Z", &ts);
  printf("Epoch is %u (%s)\n", (unsigned)timestamp, buf);
}

static unsigned int mask(unsigned u, int n_bits) {
  return u & ((1<<n_bits)-1);
}

/******************************************************************************/
static int sign_extend(unsigned u,int len) {
  if(len < 32 && u >0)
    if(u>>(len-1)&1) u |= 0xFFFFFFFF << len;
  return (int)u;
}

/******************************************************************************/
static unsigned int bits(int val, int offset, int len) {
  return mask(val >> offset,len);
}

/******************************************************************************/
static unsigned  join_bits_u(int val1, int offset1, int len1, int val2, int offset2, int len2) {
  return (bits(val1, offset1, len1) << len2) | bits(val2, offset2, len2);
}

/******************************************************************************/
static signed  join_bits_s(int val1, int offset1, int len1, int val2, int offset2, int len2) {
  return sign_extend(join_bits_u(val1, offset1, len1, val2, offset2, len2),len1+len2);
}

static void nav_save_frame(struct Space_vehicle *sv) 
{
  unsigned int unflipped[10];
  unsigned int handover_word;
  int i;
  int frame_type = 0;
  
  /* Key the initial inversion for subframe 0 off the preamble. 
     If the LSB is 0, then it is flipped */
  if(sv->navdata.new_subframe[0] & 1)
    unflipped[0] = sv->navdata.new_subframe[0];
  else
    unflipped[0] = ~sv->navdata.new_subframe[0];

  /* The next 9 depend on the value of bit 0 of the previous subframe */
  for(i = 1; i < 10; i++) {
    if(sv->navdata.new_subframe[i-1] & 1)
      unflipped[i] = ~sv->navdata.new_subframe[i];
    else
      unflipped[i] = sv->navdata.new_subframe[i];   
  }

  /* Handover word is in subframe 1 of every frame. It includes 
     the time of start for the NEXT frame. It gets held in 
     next_time_of_week till the end of frame occurs */
  handover_word = unflipped[1];
  sv->navdata.subframe_of_week = (handover_word >> 13) & 0x1FFFF; 
  sv->lock.ms_of_frame = 0;

  char buf[100];
  time_t timestamp;
  struct tm  ts;

  timestamp = TIME_EPOCH + sv->nav_time.week_no * 604800 + sv->navdata.subframe_of_week * 6;
  ts = *localtime(&timestamp);
  strftime(buf, sizeof(buf), "%a %Y-%m-%d %H:%M:%S %Z", &ts);

  
  printf("Time of next frame %i %s :",sv->navdata.subframe_of_week, buf);
  /* Handover word also includes the subframe type */
  frame_type = (handover_word >>  8) & 0x7;

  /* Now Save the required frames for later */
  printf("Frame type is %i: ",frame_type);
  for(i=0; i < 10; i++)
    printf(" %08X", unflipped[i]);
  printf("\n");

  /*if(frame_type > 0 && frame_type < 6) {
      if(sv->nav_file == NULL) {
          char name[100];
          sprintf(name, "NAV_%02i.dat",sv->id);
          sv->nav_file = fopen(name,"r+b");
          if(sv->nav_file == NULL) {
             sv->nav_file = fopen(name,"wb");
          } 
          if(sv->nav_file == NULL) {
              printf("Unable to open NAV file '%s'\n",name);
          }
      }
      if(sv->nav_file != NULL) {
          fseek(sv->nav_file, sizeof(sv->navdata.new_subframe)*(frame_type-1), SEEK_SET);
          fwrite(sv->navdata.new_subframe,sizeof(sv->navdata.new_subframe),1,sv->nav_file);
          fflush(sv->nav_file);
      }
  }*/
      
  if(frame_type == 1) {
    sv->navdata.valid_subframe[1] = 1;
      for(i = 0; i < 10; i++)
         sv->navdata.subframes[1][i] = unflipped[i];
  
      sv->nav_time.week_no              = join_bits_u(0,           0, 0, sv->navdata.subframes[1][2], 20,10);
      /* Week 524+1024 is sometime in late 2010. This will work for about 20 years after that */
      if(sv->nav_time.week_no < 524) {
        sv->nav_time.week_no += 1024*2;
      } else {
        sv->nav_time.week_no += 1024;
      }
      sv->nav_time.user_range_accuracy  = join_bits_u(0,           0, 0, sv->navdata.subframes[1][2], 14, 4);
      sv->nav_time.health               = join_bits_u(0,           0, 0, sv->navdata.subframes[1][2],  8, 6);
      sv->nav_time.group_delay     = join_bits_s(0,           0, 0, sv->navdata.subframes[1][6],  6, 8) * pow(2.0, -31.0);
      sv->nav_time.issue_of_data  = join_bits_u(sv->navdata.subframes[1][2],6, 2, sv->navdata.subframes[1][7], 22, 8);
      sv->nav_time.reference_time = join_bits_u(0,           0, 0, sv->navdata.subframes[1][7],  6,16) * pow(2.0, 4.0);
      sv->nav_time.correction_f2  = join_bits_s(0,           0, 0, sv->navdata.subframes[1][8], 22, 8) * pow(2.0, -55.0);
      sv->nav_time.correction_f1  = join_bits_s(0,           0, 0, sv->navdata.subframes[1][8],  6,16) * pow(2.0, -43.0);
      sv->nav_time.correction_f0  = join_bits_s(0,           0, 0, sv->navdata.subframes[1][9],  8,22) * pow(2.0, -31.0);
      debug_print_time(sv);
      sv->nav_time.time_good = 1;
  } else if(frame_type == 2 || frame_type == 3) {  
    unsigned iode2, iode3; 
    /* Frame 2 and 3 share common processsing */
    if(frame_type == 2) {
      sv->navdata.valid_subframe[2] = 1;
      for(i = 0; i < 10; i++)
        sv->navdata.subframes[2][i] = unflipped[i];
    } else {
      sv->navdata.valid_subframe[3] = 1;
      for(i = 0; i < 10; i++)
        sv->navdata.subframes[3][i] = unflipped[i];
    }

    /**************************************************
    * First, check that bith frames have the same Issue
    * Of Data Ephemeris values, i.e. they are havles of
    * the same data set, and that we have not already 
    * extracted the orbit parameters
    **************************************************/
    iode2               = join_bits_u(0,            0, 0, sv->navdata.subframes[2][2], 22, 8);
    iode3               = join_bits_u(0,            0, 0, sv->navdata.subframes[3][9], 22, 8);
    if(iode2 == iode3 && iode2 != sv->nav_orbit.iode) {
      /* Great! We can start extracting the fields out of the frames */
      /****************************************************
      * At most, fields are split over two subframes - so
      * we can extract them all the same, consistent way
      ****************************************************/
      /******** From FRAME 2 *******/
      sv->nav_orbit.iode        = iode2;
      sv->nav_orbit.Crs                      = join_bits_s(0,            0, 0, sv->navdata.subframes[2][2],  6,16) * pow(2.0,-5.0);
      sv->nav_orbit.delta_n                  = join_bits_s(0,            0, 0, sv->navdata.subframes[2][3], 14,16) * pow(2.0,-43.0) * PI;
      sv->nav_orbit.mean_motion_at_ephemeris = join_bits_s(sv->navdata.subframes[2][3], 6, 8, sv->navdata.subframes[2][4],  6,24) * pow(2.0,-31.0) * PI;
      sv->nav_orbit.Cuc                      = join_bits_s(0,            0, 0, sv->navdata.subframes[2][5], 14,16) * pow(2.0,-29.0);
      sv->nav_orbit.e                        = join_bits_u(sv->navdata.subframes[2][5], 6, 8, sv->navdata.subframes[2][6],  6,24) * pow(2.0,-33.0);
      sv->nav_orbit.Cus                      = join_bits_s(0,            0, 0, sv->navdata.subframes[2][7], 14,16) * pow(2.0,-29.0);
      sv->nav_orbit.sqrt_A                   = join_bits_u(sv->navdata.subframes[2][7], 6, 8, sv->navdata.subframes[2][8],  6,24) * pow(2.0,-19.0);
      sv->nav_orbit.time_of_ephemeris        = join_bits_u(0,            0, 0, sv->navdata.subframes[2][9], 14,16) * 16.0;
      sv->nav_orbit.fit_flag                 = join_bits_u(0,            0, 0, sv->navdata.subframes[2][9], 13, 1);
      sv->nav_orbit.aodo                     = join_bits_u(0,            0, 0, sv->navdata.subframes[2][9],  8, 6);

      /******** From FRAME 3 *******/
      sv->nav_orbit.Cic                      = join_bits_s(0,            0, 0, sv->navdata.subframes[3][2], 14,16) * pow(2.0,-29.0);
      sv->nav_orbit.omega_0                  = join_bits_s(sv->navdata.subframes[3][2], 6, 8, sv->navdata.subframes[3][3],  6,24) * pow(2.0,-31.0) * PI;
      sv->nav_orbit.Cis                      = join_bits_s(0,            0, 0, sv->navdata.subframes[3][4], 14,16) * pow(2.0,-29.0);
      sv->nav_orbit.inclination_at_ephemeris = join_bits_s(sv->navdata.subframes[3][4], 6, 8, sv->navdata.subframes[3][5],  6,24) * pow(2.0,-31.0) * PI;
      sv->nav_orbit.Crc                      = join_bits_s(0,            0, 0, sv->navdata.subframes[3][6], 14,16) * pow(2.0,-5.0);
      sv->nav_orbit.w                        = join_bits_s(sv->navdata.subframes[3][6], 6, 8, sv->navdata.subframes[3][7],  6,24) * pow(2.0,-31.0) * PI;
      sv->nav_orbit.omega_dot                = join_bits_s(0,            0, 0, sv->navdata.subframes[3][8],  6,24) * pow(2.0,-43.0) * PI;
      sv->nav_orbit.idot                     = join_bits_s(0,            0, 0, sv->navdata.subframes[3][9],  8,14) * pow(2.0,-43.0) * PI;
      sv->nav_orbit.orbit_valid = 1;
      debug_print_orbit(sv);
    }
  } else if(frame_type == 4) {
      sv->navdata.valid_subframe[4] = 1;
    /* Frame not used - holds almanac data */
  } else if(frame_type == 5) {
      sv->navdata.valid_subframe[5] = 1;
    /* Frame not used - holds almanac data */
  } else {
    printf("Invalid subframe type\n");
  }
}

static int nav_test_telemetry(struct Space_vehicle *sv) {
    /* TOD - mask should be 0x7FC00000A, and the first test should be against 0x5D000000 */
    
    unsigned int temp = sv->navdata.new_word & 0x3FC00000;

    /* Test the first 8 bits for for the preamble, bur also check the 
    * last bit of the previous frame to see if this one is inverted  */
    if(temp == 0x1D000000)
        return 1;
    if(temp == 0x22C00000)
        return 1;
    return 0;
}

static const unsigned char parity[32] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x13, 0x25,
    0x0B, 0x16, 0x2C, 0x19, 0x32, 0x26, 0x0E, 0x1F,
    0x3E, 0x3D, 0x38, 0x31, 0x23, 0x07, 0x0D, 0x1A,
    0x37, 0x2F, 0x1C, 0x3B, 0x34, 0x2A, 0x16, 0x29};   

static int nav_test_parity(uint_32 d)
{
    int i;
    /* 'd' holds the 32 bits received, and this function will
    * return true if the low 30 bits is a valid subframe - 
    * the most recent bit is held in bit zero */
    i = d>>30;

    /* If the last bit of the last subframe is set
    * then the data in this frame is flipped */
    if(i & 1)
        d ^= 0x3FFFFFC0;

    for(i = 6; i < 32; i++) { 
        if(d&(1<<i)) d ^= parity[i];
    }
    if((d & 0x3F) != 0) return 0;

    return 1; /* Success! */
}


static int nav_valid_subframes(struct Space_vehicle *sv) 
{
    if(!nav_test_parity(sv->navdata.new_word)) 
    {
#if SHOW_NAV_FRAMING
        printf("%02i:%5i: Parity fail\n", sv->id, sv->navdata.seq);
#endif
        return 0;
    }

    if(!sv->navdata.synced) 
    {
        if(!nav_test_telemetry(sv)) 
        {
#if SHOW_NAV_FRAMING
            printf("%02i:%5i: Telemetry fail 0x%08X\n", sv->id, sv->navdata.seq, sv->navdata.new_word );
#endif
            return 0;
        }
#if SHOW_NAV_FRAMING
        printf("%02i:%5i: Valid telemetry 0x%08X - synced\n", sv->id, sv->navdata.seq, sv->navdata.new_word );
#endif
        sv->navdata.new_subframe[sv->navdata.subframe_in_frame] = sv->navdata.new_word;
        sv->navdata.synced      = 1;
        sv->navdata.subframe_in_frame = 1;
        sv->lock.ms_of_frame      = 600;
    } else {
        if(sv->navdata.subframe_in_frame == 0) 
        {
            if(!nav_test_telemetry(sv)) 
            {
#if SHOW_NAV_FRAMING
                printf("%02i:%5i: Telemetry fail 0x%08X\n", sv->id, sv->navdata.seq, sv->navdata.new_word );
#endif
                sv->navdata.synced = 0;
                return 0;
            }
#if SHOW_NAV_FRAMING
            printf("%02i:%5i: Valid telemetry\n", sv->id, sv->navdata.seq);
#endif
            sv->navdata.new_subframe[sv->navdata.subframe_in_frame] = sv->navdata.new_word;
            sv->navdata.subframe_in_frame = 1;
        } else {
#if SHOW_NAV_FRAMING
            printf("%02i:%5i:    Subframe %i\n", sv->navdata.seq, sv->id, sv->navdata.subframe_in_frame);
#endif
            sv->navdata.new_subframe[sv->navdata.subframe_in_frame] = sv->navdata.new_word;
            if(sv->navdata.subframe_in_frame  == 9) 
            {
                nav_save_frame(sv);
                sv->navdata.subframe_in_frame = 0;
            } else 
            {
                sv->navdata.subframe_in_frame++;
            }
        }
    }
    return 1;
}


static void nav_new_bit(struct Space_vehicle *sv, uint_8 s) 
{
    /* Shift in the next bit */
    sv->navdata.new_word <<= 1;
    if(s) sv->navdata.new_word |= 1;

    sv->navdata.valid_bits++;
    if(sv->navdata.valid_bits == 32) {
        if(nav_valid_subframes(sv)) {
            sv->navdata.valid_bits = 2;
        } else {
            sv->navdata.valid_bits = 31;
        }
    }
    sv->navdata.seq++;
}

static void nav_abandon(struct Space_vehicle *sv) 
{
   // printf("%2i: Abandon - %5i errors\n", sv->id, sv->navdata.bit_errors);
    sv->navdata.valid_bits = 0;
    sv->navdata.synced = 0;
    /* Force drop if we havn't got a good bit after 'n' transistions */
    if(sv->navdata.bit_errors > MAX_BAD_BIT_TRANSITIONS)
        sv->state = state_acquiring;
    sv->navdata.bit_errors++;
}

static void nav_process(struct Space_vehicle *sv, uint_8 s)
 {
    if(sv->navdata.part_in_bit == BIT_LENGTH-1) {
        if(sv->navdata.bit_errors>0)
            sv->navdata.bit_errors--;
        sv->navdata.part_in_bit = 0;
    } else if(s != (sv->navdata.new_word&1)) {
        nav_abandon(sv);
        sv->navdata.part_in_bit = 0;
    } else
        sv->navdata.part_in_bit++;
    
    if(sv->navdata.part_in_bit == 0) {
        nav_new_bit(sv,s);
    }
}


static int nav_read_in_cached_data(struct Space_vehicle *sv) 
{
    FILE *f;
    char name[22];

    sprintf(name, "NAV_%02i.dat",sv->id);
    f = fopen(name,"r+");
    if(f == NULL) {
        printf("Unable to open NAV file '%s'\n",name);
        return 0;
    }

    while(fread(sv->navdata.new_subframe,40,1,f) == 1) {
        printf("Read in subframe\n");
        nav_save_frame(sv);
    }
    fclose(f);
    /* Reset the time_good flag, as the frame_of_week will be wrong */
    sv->nav_time.time_good = 0;
    return 1;
}


static void nav_read_in_all_cached_data(void) 
{
    int i;
    for(i = 0; i < N_SV; i++) 
    {
        nav_read_in_cached_data(space_vehicles+i);
    }
}

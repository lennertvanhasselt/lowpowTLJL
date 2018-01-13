#include "mbed.h"
#include <string>

Serial pc(SERIAL_TX, SERIAL_RX);
Serial device(PB_6, PA_10);  // D10(TX), D2(RX)
char label[6], message[256], search[6];
string temp = "GPGGA";
float buflongitude, buflatitude, longitude, latitude, timestamp, hdop, degrees, minutes;
char ns, ew;
int satUsed,lock;
bool update = false;

//Floor values
float trunc(float value) {
    if(value < 0.0) {
        value*= -1.0;
        value = floor(value);
        value*= -1.0;
    } else {
        value = floor(value);
    }
    return value;
}

//Get a new NMEA line
void getline(){
    if (device.readable()){
        //Wait for the start of a line
        if(device.getc()=='$'){
            for(int j=0; j<5; j++){
                //Stores the first 5 digits of the line
                label[j]= device.getc();
            }
            //Compare the line with the requested GPGGA, if so read out the date
            if(strcmp(label, search) == 0){
                pc.printf("GPGGA updated \r\n");
                update = true;
                for(int i=0; i<256; i++){
                    message[i] = device.getc();
                    //Stop reading when end-of-file is detected
                    if(message[i] == '\r'){
                        message[i] = 0;
                        return;
                    }
                }
                error("Overflowed message limit");
            }
        }
    }
}

void orient(){
    if(update){
        //Store the data from message in the correct variable
       if(sscanf(message,"%f,%f,%c,%f,%c,%d,%d,%f", &timestamp, &latitude, &ns, &longitude, &ew, &lock, &satUsed, &hdop) >= 1 ) {
            //When no GPS-signal is available
            if(!lock) {
                // Non-existing values
                longitude = 181.0;
                latitude = 91.0;
                satUsed = 0;
                hdop = 0;          
            } 
            //When a GPS-signal is available
            else {
                if(ns == 'S') { latitude  *= -1.0; }
                if(ew == 'W') { longitude *= -1.0; }
                //Latitude conversion in degrees
                degrees = trunc(latitude / 100.0f);
                minutes = latitude - (degrees * 100.0f);
                latitude = degrees + (minutes / 60.0f);
                //Longitude conversion in degrees    
                degrees = trunc(longitude / 100.0f);
                minutes = longitude - (degrees * 100.0f);
                longitude = degrees + (minutes / 60.0f);
            }
            //Show the received data
            if((buflongitude != longitude) & (buflatitude != latitude) & (latitude <= 90)) {
                buflongitude = longitude;
                buflatitude = latitude;
                pc.printf("You're at %f ° %c, %f ° %c \r\n", latitude, ns, longitude, ew);
                pc.printf("Based on %d satellites with a DOP of %1.2f \r\n", satUsed, hdop);
            }
        }
        update = false;
    }
}

int main() {
    //Initialize baudrate for GPS module
    device.baud(4800);
    //Create the char for comparison
    strncpy(search, temp.c_str(), sizeof(search));
    search[sizeof(search)-1] = 0;
    while(1) {
        getline();
        orient();
    }
}

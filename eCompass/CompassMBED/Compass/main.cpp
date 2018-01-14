/*
    -------------
    - E-COMPASS -
    -------------
    *Initialisation
    *While loop
        *Wait for time to wake-up (1s)
            *Enable Accelerometer
            *Enable Magnetometer
        *Wait for DRDY interrupts from magnetometer and accelerometer
            *Read data
        *When both magnetometer and accelerometer are ready to read (magDone && accDone)
            *Use accelerometer values to calculate roll, pitch and jaw
            *Use magnetometer values together with roll, pitch and jaw to calculate tilt compensated direction
            *Map values to wind directions
            *Send wind direction values in D7 command
*/

#include "mbed.h"
#include <math.h>
#include "XNucleoIKS01A2.h"

InterruptIn intAcc(D7);
InterruptIn intPinMag(D3);
InterruptIn intWakeUp(D9);
InterruptIn button(USER_BUTTON);
Ticker wakeTimer;
DigitalOut wakeGPS(D8);
DigitalOut powerD7(D10);

Serial Serial4(PC_10, PC_11, 115200);

Serial pc(USBTX, USBRX, 115200);


static XNucleoIKS01A2 *mems_expansion_board = XNucleoIKS01A2::instance(D14, D15, D4, D5);
static LSM303AGRMagSensor *magnetometer = mems_expansion_board->magnetometer;
static LSM303AGRAccSensor *accelerometer = mems_expansion_board->accelerometer;

volatile bool magReady = false;
volatile bool accReady=false;
volatile bool timerReady=false;
volatile bool wakeReady=true;
volatile bool magDone = false;
volatile bool accDone=false;
volatile bool D7Ready=false;
volatile bool shutdown=false;
volatile bool buttonPress=false;
volatile char read;

/* Defines */
#define X 0
#define Y 1
#define Z 2

/* Interrupt Handlers */
void accHandle(){
    accReady=true;
}

void buttonHandle(){
    D7Ready=true;
    buttonPress=true;
}

void timerHandle(){
    timerReady=true;
}

void magHandle(){
    magReady=true;
}

void D7Handle(){
    read=Serial4.getc();
    D7Ready=true;
}

void wakeHandle(){
    wakeReady=true;   
}

/* Initialisation Magnetometer  */
void initMag(uint8_t id, int32_t Maxes[3], float *hardCor){
    LSM303AGR_MAG_W_LP(magnetometer, LSM303AGR_MAG_LP_MODE);                //Enables low power mode
    LSM303AGR_MAG_W_OFF_CANC(magnetometer, LSM303AGR_MAG_OFF_CANC_DISABLED);//Disable offset cancellation
    LSM303AGR_MAG_W_INT_MAG(magnetometer, LSM303AGR_MAG_INT_MAG_ENABLED);   //Enable DRDY signal
    intPinMag.mode(PullDown);                                               //Interrupt pin on Pulldown
    LSM303AGR_MAG_W_MD(magnetometer, LSM303AGR_MAG_MD_SINGLE_MODE );        //Single mode, 1 measurement performed
    
    //Hard iron correction calculation  
    //Source: https://github.com/kriswiner/MPU6050/wiki/Simple-and-Effective Magnetometer-Calibration  
     uint16_t ii = 0, sample_count = 0;  
      int16_t mag_temp[3] = {0, 0, 0}, mag_max[3] = {-32767, -32767, -32767}, mag_min[3] = {32767, 32767, 32767};  
      int32_t mag_bias[3] = {0, 0, 0}, mag_scale[3] = {0, 0, 0};  
      float sensitivity = 1.5f;  
      sample_count = 30;  
        
      magnetometer->enable();  
       
    //Get the max and min values of X,Y & Z by taking sample_count amount of samples
     for(ii = 0; ii < sample_count; ii++) {  
         magnetometer->get_m_axes_raw(mag_temp);     
         for (int jj = 0; jj < 3; jj++) {  
             if(mag_temp[jj] > mag_max[jj]) mag_max[jj] = mag_temp[jj];  
             if(mag_temp[jj] < mag_min[jj]) mag_min[jj] = mag_temp[jj];  
         }  
         //pc.printf("move it \r\n");  
         wait(1);  
     }  
       
     //Get hard iron correction by taking average  
     mag_bias[X]  = (mag_max[X] + mag_min[X])/2;  //get average x mag bias in counts
     mag_bias[Y]  = (mag_max[Y] + mag_min[Y])/2;  //get average y mag bias in counts
     mag_bias[Z]  = (mag_max[Z] + mag_min[Z])/2;  //get average z mag bias in counts
      
     //Save mag_biases in hardCor for main program   
     hardCor[X] = (float) mag_bias[X] * sensitivity;  
     hardCor[Y] = (float) mag_bias[Y] * sensitivity;     
     hardCor[Z] = (float) mag_bias[Z] * sensitivity;    
     
     /*Get soft iron correction
     mag_scale[0]  = (mag_max[0] - mag_min[0])/2;  // get average x axis max chord length in counts
     mag_scale[1]  = (mag_max[1] - mag_min[1])/2;  // get average y axis max chord length in counts
     mag_scale[2]  = (mag_max[2] - mag_min[2])/2;  // get average z axis max chord length in counts
    
     float avg_rad = mag_scale[0] + mag_scale[1] + mag_scale[2];
     avg_rad /= 3.0;
     
     softCor[0] = avg_rad/((float)mag_scale[0]);
     softCor[1] = avg_rad/((float)mag_scale[1]);
     softCor[2] = avg_rad/((float)mag_scale[2]);
     
     //pc.printf("Soft Iron Correction:  %f, %f, %f\r\n", softCor[X], softCor[Y], softCor[Z]);  
     */ 

    //Put magnetometer back in single mode (1 measurement)
    LSM303AGR_MAG_W_MD(magnetometer, LSM303AGR_MAG_MD_SINGLE_MODE );
    magnetometer->get_m_axes(Maxes);
    magnetometer->disable();
    magnetometer->read_id(&id);
}

/* Initialisation Accelerometer */
void initAcc(uint8_t id, int32_t Aaxes[3]){
    //Init Acc
    LSM303AGR_ACC_W_LOWPWR_EN(accelerometer, LSM303AGR_ACC_LPEN_ENABLED);               //Enable Low power
    accelerometer->set_x_odr(1);                                                        //ODR to 1
    LSM303AGR_ACC_W_FIFO_DRDY1_on_INT1(accelerometer, LSM303AGR_ACC_I1_DRDY1_ENABLED);  //Enable DRDY interrupt
    LSM303AGR_ACC_W_IntActive(accelerometer, LSM303AGR_ACC_H_LACTIVE_ACTIVE_HI);        //Enable interrupts (default)
    
    accelerometer->enable();            
    accelerometer->get_x_axes(Aaxes);   //Read before activating, otherwise program won't trigger (DRDY is already high when started)
    accelerometer->disable();
    accelerometer->read_id(&id);
}

/* Send ALP command bytes over UART */
void sendBytes(uint8_t data)
{
    //Send ALP header
    uint8_t ALP[] = {                                   //QOS=0, Multicast, AC=0x01
        0x41, 0x54, 0x24, 0x44, 0xc0, 0x00,             // Serial interface
        0x0d,                                           // ALP CMD LENGTH (from the next byte untill the last data byte)
        0xb4, 0x13, 0x32, 0xd7, 0x00, 0x00, 0x10, 0x01, // FORWARD + OPERAND
        0x20, 0x40, 0x00                                // RETURN FILE DATA ACTION, FILEID 40, OFFSET 0
    }; 
    
    for(int i=0; i<sizeof(ALP); i++)        
    {
        Serial4.printf("%c", ALP[i]);
    }

    Serial4.printf("%c",0x01);  // Send length of data
    Serial4.printf("%c", data); // Send data
}

int main() {
    uint8_t id;
    int32_t Aaxes[3];
    int32_t Maxes[3];
    float roll_rad=0, pitch_rad=0;
    float yaw_rad=0, degree=0, godr=0;
    float temp[3] = {}, hardCor[3] = {};
    /*      Only initialise when waken up
    //Initialisation interrupts
    intPinMag.rise(&magHandle);
    intAcc.mode(PullDown);
    intAcc.rise(&accHandle);
    intWakeUp.rise(&wakeHandle);
    wakeTimer.attach(&timerHandle, 1); //(function, time in seconds)
    
    initMag(id, Maxes, hardCor);
    initAcc(id, Aaxes);
    
    Serial4.attach(&Rx_interrupt, Serial::RxIrq); // Setup a serial interrupt function to receive data
    */
    
    while(1) {
        if(wakeReady) {
            //pc.printf("Wakey wakey!\r\n");  
            //Initialisation interrupts
            powerD7=1;  
            wakeGPS=0;
            
            initMag(id, Maxes, hardCor);
            initAcc(id, Aaxes);
            
            intPinMag.rise(&magHandle);
            button.rise(&buttonHandle);
            intAcc.mode(PullDown);
            intAcc.rise(&accHandle);
            intWakeUp.rise(NULL);
            wakeTimer.attach(&timerHandle, 1); //(function, time in seconds)
            
            Serial4.attach(&D7Handle, Serial::RxIrq); // Setup a serial interrupt function to receive data
            wakeReady=false;
        }
        /* Enable sensors when timerReady interrupt is received */
        if(timerReady) {
            accDone=false;
            magDone=false;
            
            //Wake up sensors
            magnetometer->enable();
            accelerometer->enable(); 
            
            //Putting magnemtometer in single mode
            LSM303AGR_MAG_W_MD(magnetometer, LSM303AGR_MAG_MD_SINGLE_MODE );            
            timerReady=false;
        }
        /* Get accelerometer values when accReady interrupt is received */
        if(accReady) {
            accelerometer->get_x_axes(Aaxes);
            
            accDone=true;
            accReady=false;
            accelerometer->disable();
        }
        /* Get magnetometer values when magReady interrupt is received */
        if(magReady){
            magnetometer->get_m_axes(Maxes);
            
            //Apply hard iron correction to the received values
            Maxes[X] = Maxes[X]-hardCor[X];
            Maxes[Y] = Maxes[Y]-hardCor[Y];
            Maxes[Z] = Maxes[Z]-hardCor[Z];
            
            magDone=true;
            magReady=false;
            magnetometer->disable();
        }
        /* When both accelerometer and magnetometer are done reading, start calculations*/
        if(magDone && accDone){
            //Source for calculating roll, pitch and yaw
            //http://www.st.com/content/ccc/resource/technical/document/design_tip/group0/56/9a/e4/04/4b/6c/44/ef/DM00269987/files/DM00269987.pdf/jcr:content/translations/en.DM00269987.pdf
            roll_rad=atan2((float)Aaxes[Y],Aaxes[Z]);
            
            temp[0]=(float)Aaxes[Y]*sin(roll_rad);
            temp[1]=cos(roll_rad)*(float)Aaxes[Z]+temp[0];
            pitch_rad=-atan2((float)Aaxes[X],sqrt( pow((float)Aaxes[Y],2) +  pow((float)Aaxes[Z],2)));//temp[1]);
            
            //Determining where the head of the compass is pointed at
            temp[0]=Maxes[Z]*sin(roll_rad)-Maxes[Y]*cos(roll_rad);
            temp[1]=Maxes[Y]*sin(roll_rad)+Maxes[Z]*cos(roll_rad);
            temp[2]=Maxes[X]*cos(pitch_rad)+temp[1]*sin(pitch_rad);
            yaw_rad=atan2((float)temp[0],temp[2]);
            degree=yaw_rad*57.296; //180/PI
            
            //Transforming degrees into a wind direction, which results into a direction value
            //The direction value will be send with Dash7 to the backend.
            uint8_t direction;
            if(degree > 360) {
            degree = degree-360;
            }
            if(degree < 0) {
                degree = degree+360;    
            }
            if(degree > 22.5 && degree < 67.5) {
                direction = 1;                          //NE
            }
            else if(degree > 67.5 && degree < 112.5) {
                direction = 2;                          //E
            }
            else if(degree > 112.5 && degree < 157.5) {
                direction = 3;                          //SE
            }
            else if(degree > 157.5 && degree < 202.5) {
                direction = 4;                          //S
            } 
            else if(degree > 202.5 && degree < 247.5) {
                direction = 5;                          //SW
            }
            else if(degree > 247.5 && degree < 292.5) {
                direction = 6;                          //W
            }
            else if(degree > 292.5 && degree < 337.25) {
                direction = 7;                          //NW
            }                      
            else if(degree > 337.25 || degree < 22.5) {
                direction = 0;                          //W
            }
            //pc.printf("degree: %d\r\n", direction);
            magnetometer->get_m_odr(&godr);
            sendBytes(direction);
            
            magDone=false;
            accDone=false;
        }
        if(D7Ready) // ISR to read in data from serial port
        {
            if(buttonPress) {
            //if(read == '3')
                buttonPress=false;
                shutdown = true;// enable GPS via other UART (wired with jumpers)
            }
            D7Ready = false;
        }
        if(shutdown) {
            //pc.printf("shut it! \r\n");  
            //Initialisation interrupts
            intPinMag.rise(NULL);
            intAcc.rise(NULL);
            intWakeUp.rise(&wakeHandle);
            wakeTimer.attach(NULL, 1); //(function, time in seconds)
            
            magnetometer->disable();
            accelerometer->disable();
            
            Serial4.attach(NULL, Serial::RxIrq); // Setup a serial interrupt function to receive data
            
            powerD7=0;
            wakeGPS=1;
            wait_ms(50);
            wakeGPS=0;
            
            shutdown=false;
        }
        
        
            
        //When no interrupts are present let the device sleep
        sleep();
    }
}
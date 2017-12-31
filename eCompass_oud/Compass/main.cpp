#include "mbed.h"
#include <math.h>
#include "XNucleoIKS01A2.h"

InterruptIn intAcc(D7);
InterruptIn intPinMag(D3);
Ticker wakeTimer;

static XNucleoIKS01A2 *mems_expansion_board = XNucleoIKS01A2::instance(D14, D15, D4, D5);
static LSM303AGRMagSensor *magnetometer = mems_expansion_board->magnetometer;
static LSM303AGRAccSensor *accelerometer = mems_expansion_board->accelerometer;

volatile bool magReady = false;
volatile bool accReady=false;
volatile bool timerReady=false;
volatile bool magDone = false;
volatile bool accDone=false;

/* Defines */
#define X 0
#define Y 1
#define Z 2

/* Interrupt Handlers */
void accHandle(){
    accReady=true;
}

void timerHandle(){
    timerReady=true;
}

void magHandle(){
    magReady=true;
}

/* Initialisation Magnetometer  */
void initMag(uint8_t id, int32_t Maxes[3], float *hardCor){
    LSM303AGR_MAG_W_LP(magnetometer, LSM303AGR_MAG_LP_MODE);                //Enables low power mode
    LSM303AGR_MAG_W_OFF_CANC(magnetometer, LSM303AGR_MAG_OFF_CANC_DISABLED);//Disable offset cancellation
    LSM303AGR_MAG_W_INT_MAG(magnetometer, LSM303AGR_MAG_INT_MAG_ENABLED);   //Enable DRDY signal
    intPinMag.mode(PullDown);                                               //Interrupt pin on Pulldown
    LSM303AGR_MAG_W_MD(magnetometer, LSM303AGR_MAG_MD_SINGLE_MODE );        //Single mode, 1 measurement performed
    
    //Hard iron correction calculation
    //Source: https://github.com/kriswiner/MPU6050/wiki/Simple-and-Effective-Magnetometer-Calibration
    uint16_t ii = 0, sample_count = 0;
    int32_t mag_bias[3] = {0, 0, 0};
    int32_t mag_max[3] = {-2147483647, -2147483647, -2147483647}, mag_min[3] = {2147483647, 2147483647, 2147483647}, mag_temp[3] = {0, 0, 0};
    sample_count = 30;
    
    magnetometer->enable();
    
    //Get the max and min values of X,Y & Z by taking sample_count amount of samples
    for(ii = 0; ii < sample_count; ii++) {
        magnetometer->get_m_axes(mag_temp);   
        for (int jj = 0; jj < 3; jj++) {
            if(mag_temp[jj] > mag_max[jj]) mag_max[jj] = mag_temp[jj];
            if(mag_temp[jj] < mag_min[jj]) mag_min[jj] = mag_temp[jj];
        }
        printf("Move that device like a pretzel!\r\n");
        wait(1);
    }
    
    //Get hard iron correction by taking average
    mag_bias[X]  = (mag_max[X] + mag_min[X])/2;  // get average x mag bias in counts
    mag_bias[Y]  = (mag_max[Y] + mag_min[Y])/2;  // get average y mag bias in counts
    mag_bias[Z]  = (mag_max[Z] + mag_min[Z])/2;  // get average z mag bias in counts
    
    //Save mag_biases in hardCor for main program 
    hardCor[X] = mag_bias[X];
    hardCor[Y] = mag_bias[Y];   
    hardCor[Z] = mag_bias[Z];

    //Put magnetometer back in single mode (1 measurement)
    LSM303AGR_MAG_W_MD(magnetometer, LSM303AGR_MAG_MD_SINGLE_MODE );
    magnetometer->get_m_axes(Maxes);
    magnetometer->disable();
    
    magnetometer->read_id(&id);
    printf("LSM303AGR magnetometer            = 0x%X\r\n", id);
}

/* Initialisation Accelerometer */
void initAcc(uint8_t id, int32_t Aaxes[3]){
    //init Acc
    LSM303AGR_ACC_W_LOWPWR_EN(accelerometer, LSM303AGR_ACC_LPEN_ENABLED);
    accelerometer->set_x_odr(1);
    LSM303AGR_ACC_W_FIFO_DRDY1_on_INT1(accelerometer, LSM303AGR_ACC_I1_DRDY1_ENABLED);
    LSM303AGR_ACC_W_IntActive(accelerometer, LSM303AGR_ACC_H_LACTIVE_ACTIVE_HI); //default
    
    accelerometer->enable();
    accelerometer->get_x_axes(Aaxes);
    accelerometer->disable();
    
    accelerometer->read_id(&id);
    printf("\r\n LSM303AGR accelerometer           = 0x%X\r\n", id);
}

int main() {
    uint8_t id;
    int32_t Aaxes[3];
    int32_t Maxes[3];
    float roll=0, pitch=0, roll_rad=0, pitch_rad=0;
    float yaw_rad=0, degree=0, godr=0;
    float temp[3] = {}, hardCor[3] = {};
    
    //Initialisation interrupts
    intPinMag.rise(&magHandle);
    intAcc.mode(PullDown);
    intAcc.rise(&accHandle);
    wakeTimer.attach(&timerHandle, 1); //(function, time in seconds)
    
    initMag(id, Maxes, hardCor);
    initAcc(id, Aaxes);
    
    while(1) {
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
            printf("LSM303AGR [mag/mgauss]:  %f, %f, %f\r\n", hardCor[X], hardCor[Y], hardCor[Z]);
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
            printf("\r\n");
            roll_rad=atan2((float)Aaxes[Y],Aaxes[Z]);
            roll=roll_rad*57.296;
            
            temp[0]=(float)Aaxes[Y]*sin(roll_rad);
            temp[1]=cos(roll_rad)*(float)Aaxes[Z]+temp[0];
            pitch_rad=-atan2((float)Aaxes[X],sqrt( pow((float)Aaxes[Y],2) +  pow((float)Aaxes[Z],2)));//temp[1]);
            pitch=pitch_rad*57.296;
            printf("Angle: roll: %6lf   pitch: %6lf \r\n ",roll,pitch);
            
            //Determining where the head of the compass is pointed at
            temp[0]=Maxes[Z]*sin(roll_rad)-Maxes[Y]*cos(roll_rad);
            temp[1]=Maxes[Y]*sin(roll_rad)+Maxes[Z]*cos(roll_rad);
            temp[2]=Maxes[X]*cos(pitch_rad)+temp[1]*sin(pitch_rad);
            yaw_rad=atan2((float)temp[0],temp[2]);
            degree=yaw_rad*57.296; //180/PI
            
            //Transforming degrees into a wind direction
            if(degree > 360) {
            degree = degree-360;
            }
            if(degree < 0) {
                degree = degree+360;    
            }
            printf("degree: %lf\r\n", degree);
            if(degree > 22.5 && degree < 67.5) {
                printf("Direction: North-East\r\n");
            }
            else if(degree > 67.5 && degree < 112.5) {
                printf("Direction: East\r\n");
            }
            else if(degree > 112.5 && degree < 157.5) {
                printf("Direction: South-East\r\n");
            }
            else if(degree > 157.5 && degree < 202.5) {
                printf("Direction: South\r\n");
            } 
            else if(degree > 202.5 && degree < 247.5) {
                printf("Direction: South-West\r\n");
            }
            else if(degree > 247.5 && degree < 292.5) {
                printf("Direction: West\r\n");
            }
            else if(degree > 292.5 && degree < 337.25) {
                printf("Direction: North-West\r\n");
            }                      
            else if(degree > 337.25 || degree < 22.5) {
                printf("Direction: North\r\n");
            }
            printf("LSM303AGR [mag/mgauss]:  %6ld, %6ld, %6ld\r\n", Maxes[X], Maxes[Y], Maxes[Z]);
            magnetometer->get_m_odr(&godr);
            printf("ODR-type: %10f\r\n",godr);
            
            magDone=false;
            accDone=false;
        }
        //When no interrupts are present let the device sleep
        sleep();
    }
}



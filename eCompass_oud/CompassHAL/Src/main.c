/**
  ******************************************************************************
  * File Name          : main.c
  * Description        : Main program body
  ******************************************************************************
  ** This notice applies to any and all portions of this file
  * that are not between comment pairs USER CODE BEGIN and
  * USER CODE END. Other portions of this file, whether 
  * inserted by the user or by software development tools
  * are owned by their respective copyright owners.
  *
  * COPYRIGHT(c) 2017 STMicroelectronics
  *
  * Redistribution and use in source and binary forms, with or without modification,
  * are permitted provided that the following conditions are met:
  *   1. Redistributions of source code must retain the above copyright notice,
  *      this list of conditions and the following disclaimer.
  *   2. Redistributions in binary form must reproduce the above copyright notice,
  *      this list of conditions and the following disclaimer in the documentation
  *      and/or other materials provided with the distribution.
  *   3. Neither the name of STMicroelectronics nor the names of its contributors
  *      may be used to endorse or promote products derived from this software
  *      without specific prior written permission.
  *
  * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
  * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
  * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
  * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
  * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
  * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
  * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
  * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  *
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "stm32l1xx_hal.h"

/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private variables ---------------------------------------------------------*/
I2C_HandleTypeDef hi2c1;
TIM_HandleTypeDef htim3;
UART_HandleTypeDef huart2;

/* USER CODE BEGIN PV */
/* Private variables ---------------------------------------------------------*/
#define accAddress (0x19 << 1)
//#define magAddress (0x3C)  //(0x1E << 1)
//#define OUTX_L 0x68
//#define OUTX_H 0x69
#define OUTY_L 0x6A
#define OUTY_H 0x6B
#define OUTZ_L 0x6C
#define OUTZ_H 0x6D
#define X 0
#define Y 1
#define Z 2
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_I2C1_Init(void);
static void MX_TIM3_Init(void);
static void MX_USART2_UART_Init(void);

/* USER CODE BEGIN PFP */
/* Private function prototypes -----------------------------------------------*/

/* USER CODE END PFP */

/* USER CODE BEGIN 0 */

/* USER CODE END 0 */
uint8_t read_from_mag(uint16_t addr)
{
	uint8_t buffer[] = {addr};
	uint8_t value;
	uint8_t magAddress = (0x19 << 1);

	while (HAL_I2C_GetState(&hi2c1) != HAL_I2C_STATE_READY || HAL_I2C_IsDeviceReady(&hi2c1, magAddress, 3, 100) != HAL_OK)
	{	HAL_UART_Transmit(&huart2,(uint8_t*)"\r\nNot Ready",sizeof("\r\nNot Ready"),HAL_MAX_DELAY);
	}
	while (HAL_I2C_Master_Transmit(&hi2c1,                // i2c handle
								  magAddress,    		  // i2c address, left aligned
	                              (uint8_t *)&buffer,     // data to send
	                              2,                      // how many bytes - 16 bit register address = 2 bytes
	                              100)                    // timeout
	                              	  != HAL_OK)          // result code
	{
		if (HAL_I2C_GetError(&hi2c1) != HAL_I2C_ERROR_AF)
		{
			Error_Handler();
		}
	}
	while (HAL_I2C_IsDeviceReady(&hi2c1, magAddress, 3, 100) != HAL_OK) {
		HAL_UART_Transmit(&huart2,(uint8_t*)"\r\nNot Ready3",sizeof("\r\nNot Ready3"),HAL_MAX_DELAY);
	}
	while (HAL_I2C_Master_Receive(&hi2c1,            	// i2c handle
								 magAddress,    		// i2c address, left aligned
								 (uint8_t *)&value,   	// pointer to address of where to store received data
								 1,                   	// expecting one byte to be returned
								 100)                	// timeout
								 	 != HAL_OK)       	// result code
	{
		HAL_UART_Transmit(&huart2,(uint8_t*)"\r\nNot Ready",sizeof("\r\nNot Ready"),HAL_MAX_DELAY);
		if (HAL_I2C_GetError (&hi2c1) != HAL_I2C_ERROR_AF)
		{
			Error_Handler();
		}
	}
	return value;
}


int32_t * get_axes(int32_t mag_temp[]){
	uint8_t XL=0, XH=0;
	uint8_t YL=0, YH=0;
	uint8_t ZL=0, ZH=0;
	uint8_t magAddress = 0x1E << 1; //Shift to the left 0x3C
	uint16_t OUTX_L = 0x68;
	uint16_t OUTX_H = 0x69;
	// OUTX_H, OUTY_L, OUTY_H, OUTZ_L, OUTZ_H;

	if(HAL_I2C_IsDeviceReady(&hi2c1, magAddress, 5, HAL_MAX_DELAY) == HAL_OK){
		HAL_UART_Transmit(&huart2,(uint8_t*)"Ready: ",sizeof("Ready: "),HAL_MAX_DELAY);
	}
	//XL=read_from_mag(OUTX_L);
	//XH=read_from_mag(OUTX_H);
	HAL_I2C_Mem_Read(&hi2c1, magAddress, OUTX_L, I2C_MEMADD_SIZE_8BIT,&XL,sizeof(XL),HAL_MAX_DELAY);
	HAL_I2C_Mem_Read(&hi2c1, magAddress, OUTX_H, I2C_MEMADD_SIZE_8BIT,&XH,sizeof(XH),HAL_MAX_DELAY);
	HAL_I2C_Mem_Read(&hi2c1, magAddress, OUTY_L, I2C_MEMADD_SIZE_8BIT,&YL,sizeof(YL),HAL_MAX_DELAY);
	HAL_I2C_Mem_Read(&hi2c1, magAddress, OUTY_H, I2C_MEMADD_SIZE_8BIT,&YH,sizeof(YH),HAL_MAX_DELAY);
	HAL_I2C_Mem_Read(&hi2c1, magAddress, OUTZ_L, I2C_MEMADD_SIZE_8BIT,&ZL,sizeof(ZL),HAL_MAX_DELAY);
	HAL_I2C_Mem_Read(&hi2c1, magAddress, OUTZ_H, I2C_MEMADD_SIZE_8BIT,&ZH,sizeof(ZH),HAL_MAX_DELAY);

	HAL_UART_Transmit(&huart2,&XL,sizeof(XH),HAL_MAX_DELAY);
	HAL_UART_Transmit(&huart2,&XL,sizeof(XL),HAL_MAX_DELAY);
	HAL_UART_Transmit(&huart2,(uint8_t*)" end \n\r",sizeof(" end \n\r"),HAL_MAX_DELAY);

	mag_temp[1] = (int32_t)(((XH << 8) | (XL & 0xff))*1.5);
	mag_temp[2] = (int32_t)(((YH << 8) | (YL & 0xff))*1.5);
	mag_temp[3] = (int32_t)(((ZH << 8) | (ZL & 0xff))*1.5);
	return *mag_temp;
}
void calibration(int32_t Maxes[3], float *hardCor){
	  uint16_t ii = 0, sample_count = 30;
	  int32_t mag_bias[3] = {0, 0, 0};
	  int32_t mag_max[3] = {-2147483647, -2147483647, -2147483647}, mag_min[3] = {2147483647, 2147483647, 2147483647}, mag_temp[3] = {0, 0, 0};
	  //Get the max and min values of X,Y & Z by taking sample_count amount of samples
	  for(ii = 0; ii < sample_count; ii++) {
		  *mag_temp=get_axes(mag_temp);
		  //magnetometer->get_m_axes(mag_temp);
	      for (int jj = 0; jj < 3; jj++) {
	    	  if(mag_temp[jj] > mag_max[jj]) mag_max[jj] = mag_temp[jj];
	          if(mag_temp[jj] < mag_min[jj]) mag_min[jj] = mag_temp[jj];
	      }
	      HAL_UART_Transmit(&huart2,(uint8_t*)mag_max[3],sizeof(mag_max[3]),HAL_MAX_DELAY);
	      HAL_UART_Transmit(&huart2,(uint8_t*)"Move that device like a pretzel! \n\r",sizeof("Move that device like a pretzel! \n\r"),HAL_MAX_DELAY);
	      HAL_Delay(1000);
	  }

	  //Get hard iron correction by taking average
	  mag_bias[X]  = (mag_max[X] + mag_min[X])/2;  // get average x mag bias in counts
	  mag_bias[Y]  = (mag_max[Y] + mag_min[Y])/2;  // get average y mag bias in counts
	  mag_bias[Z]  = (mag_max[Z] + mag_min[Z])/2;  // get average z mag bias in counts

	  //Save mag_biases in hardCor for main program
	  hardCor[X] = (float) mag_bias[X];
	  hardCor[Y] = (float) mag_bias[Y];
	  hardCor[Z] = (float) mag_bias[Z];
 }

void initMag(void)
{
	uint8_t CFG_REG_A_M_Data;
	uint8_t magAddress = 0x3C;
	//Enable DRDY
	CFG_REG_A_M_Data=0x00;
	//CFG_REG_A_M_Data &= ~0x03; CFG_REG_A_M_Data |= 0x01;
	HAL_I2C_Mem_Write(&hi2c1,magAddress,0x20,sizeof(0x20),CFG_REG_A_M_Data,sizeof(CFG_REG_A_M_Data),0xFFFFFFFF);

	//Enable CONTINUOUS MODE
	CFG_REG_A_M_Data=0x00;
	HAL_I2C_Mem_Write(&hi2c1,magAddress,0x60,sizeof(0x60),CFG_REG_A_M_Data,sizeof(CFG_REG_A_M_Data),0xFFFFFFFF);

	//Enable LoPow
	CFG_REG_A_M_Data=read_from_mag(0x60);
	CFG_REG_A_M_Data &= ~0x10; CFG_REG_A_M_Data |= 0x10;
	HAL_I2C_Mem_Write(&hi2c1,magAddress,0x60,sizeof(0x60),CFG_REG_A_M_Data,sizeof(CFG_REG_A_M_Data),0xFFFFFFFF);

	//Disable Offset
	CFG_REG_A_M_Data=read_from_mag(0X61);
	CFG_REG_A_M_Data &= ~0x02; //CFG_REG_A_M_Data |= 0x00;
	HAL_I2C_Mem_Write(&hi2c1,magAddress,0X61,sizeof(0X61),CFG_REG_A_M_Data,sizeof(CFG_REG_A_M_Data),0xFFFFFFFF);

	//Enable DRDY
	CFG_REG_A_M_Data=read_from_mag(0X62);
	CFG_REG_A_M_Data &= ~0x01; CFG_REG_A_M_Data |= 0x01;
	HAL_I2C_Mem_Write(&hi2c1,magAddress,0X62,sizeof(0X62),CFG_REG_A_M_Data,sizeof(CFG_REG_A_M_Data),0xFFFFFFFF);
}

int main(void)
{
	uint8_t id;
	int32_t Aaxes[3];
	int32_t Maxes[3];
	uint8_t magAddress = 0x1E << 1; //Shift to the left 0x3C
	float roll=0, pitch=0, roll_rad=0, pitch_rad=0;
	float yaw_rad=0, degree=0, godr=0;
	float temp[3] = {}, hardCor[3] = {};
	/* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration----------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_I2C1_Init();
  MX_TIM3_Init();
  MX_USART2_UART_Init();

  /* USER CODE BEGIN 2 */

  /* USER CODE END 2 */

  //Low power, continuous mode with 100Hz ODR
  char CFG_REG_A_M_Data = 0b00011100;
  HAL_I2C_Mem_Write(&hi2c1,magAddress,0x60,sizeof(0x60),(uint8_t*)CFG_REG_A_M_Data,sizeof(CFG_REG_A_M_Data),0xFFFFFFFF);
  initMag();
  calibration(Maxes, hardCor);
  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
  /* USER CODE END WHILE */
//  *Maxes=get_axes(Maxes);
//  Maxes[X] = Maxes[X]-hardCor[X];
//  Maxes[Y] = Maxes[Y]-hardCor[Y];
//  Maxes[Z] = Maxes[Z]-hardCor[Z];

  HAL_Delay(1500);
  /* USER CODE BEGIN 3 */

  }
  /* USER CODE END 3 */

}

/** System Clock Configuration
*/
void SystemClock_Config(void)
{

  RCC_OscInitTypeDef RCC_OscInitStruct;
  RCC_ClkInitTypeDef RCC_ClkInitStruct;

    /**Configure the main internal regulator output voltage 
    */
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

    /**Initializes the CPU, AHB and APB busses clocks 
    */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = 16;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL6;
  RCC_OscInitStruct.PLL.PLLDIV = RCC_PLL_DIV3;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

    /**Initializes the CPU, AHB and APB busses clocks 
    */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

    /**Configure the Systick interrupt time 
    */
  HAL_SYSTICK_Config(HAL_RCC_GetHCLKFreq()/1000);

    /**Configure the Systick 
    */
  HAL_SYSTICK_CLKSourceConfig(SYSTICK_CLKSOURCE_HCLK);

  /* SysTick_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(SysTick_IRQn, 0, 0);
}

/* I2C1 init function */
static void MX_I2C1_Init(void)
{

  hi2c1.Instance = I2C1;
  hi2c1.Init.ClockSpeed = 100000;
  hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

}

/* TIM3 init function */
static void MX_TIM3_Init(void)
{

  TIM_ClockConfigTypeDef sClockSourceConfig;
  TIM_MasterConfigTypeDef sMasterConfig;

  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 0;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 0;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  if (HAL_TIM_Base_Init(&htim3) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim3, &sClockSourceConfig) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

}

/* USART2 init function */
static void MX_USART2_UART_Init(void)
{

  huart2.Instance = USART2;
  huart2.Init.BaudRate = 9600;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

}

/** Configure pins as 
        * Analog 
        * Input 
        * Output
        * EVENT_OUT
        * EXTI
*/
static void MX_GPIO_Init(void)
{

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @param  None
  * @retval None
  */
void _Error_Handler(char * file, int line)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  while(1) 
  {
  }
  /* USER CODE END Error_Handler_Debug */ 
}

#ifdef USE_FULL_ASSERT

/**
   * @brief Reports the name of the source file and the source line number
   * where the assert_param error has occurred.
   * @param file: pointer to the source file name
   * @param line: assert_param error line source number
   * @retval None
   */
void assert_failed(uint8_t* file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
    ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */

}

#endif

/**
  * @}
  */ 

/**
  * @}
*/ 

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
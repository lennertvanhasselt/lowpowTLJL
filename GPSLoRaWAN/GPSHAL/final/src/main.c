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
#include <stdio.h>
#include <string.h>

/* Private variables ---------------------------------------------------------*/
I2C_HandleTypeDef hi2c1;
UART_HandleTypeDef huart1;
UART_HandleTypeDef huart2;
UART_HandleTypeDef huart3;
int notEnabled = 1, enableCompass = 0;

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_USART2_UART_Init(void);
static void MX_USART3_UART_Init(void);
static void MX_I2C1_Init(void);
static void sendCoord(void);
static void initGPS(void);
static void enterSleep(uint32_t regulator);

int main(void)
{

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* Configure the system clock */
  SystemClock_Config();

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART1_UART_Init();
  MX_USART2_UART_Init();
  MX_USART3_UART_Init();
  MX_I2C1_Init();

  /* Initialize GPS to send specific data on specific date in time. */
  initGPS();

  /* Infinite loop */
  while (1)
  {
	  /*
	   * When the user button (PC_13) is pressed, the GPS power will be cut down.(PC_7)
	   * additionally, a short pulse (100ms) will be send to the compass (PB_6) in order to enable it.
	   */
	  if(enableCompass)
	  {
			notEnabled = 1;
			HAL_GPIO_WritePin(GPIOC, GPIO_PIN_7, GPIO_PIN_RESET);
			HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_SET);
			for(int i=0; i<65535; i++);
			HAL_Delay(100);
			HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_RESET);
			enableCompass = 0;
	  }

	  /*
	   * When the Nucleo receives a pulse from the compass (PA_8), the power supply to the GPS (PC_7)
	   * will be enabled. This leads to the reading of GPS values.
	   * When the pulse is not yet given, the system will be asleep.
	   */
	  while(notEnabled)
	  {
		  HAL_UART_Transmit(&huart2, "Not yet \n\r",sizeof("Not yet \n\r"), HAL_MAX_DELAY);
		  /* Low power sleep mode with longer wake up time compared to "PWR_MAINREGULATOR_ON" */
		  enterSleep(PWR_LOWPOWERREGULATOR_ON);
	  }

	  /* Lower power regulator mode for the system, its system frequency will not exceed 2MHz (ref. Mastering STM32 p536)*/
	  HAL_PWREx_EnableLowPowerRunMode();
	  HAL_UART_Transmit(&huart2, "Enter the underworld \n\r",sizeof("Enter the underworld \n\r"), HAL_MAX_DELAY);

	  /* Function where GPS data will be parsed and send */
	  sendCoord();
	}
}

/* In order to receive the correct data and limit the unwanted forms, data will be send to the GPS-module*/
void initGPS()
{
	//uint8_t setGPGGA[] = {0x24, 0x50, 0x53, 0x52, 0x46, 0x31, 0x30, 0x33, 0x2c, 0x30, 0x30, 0x2c, 0x30, 0x30, 0x2c, 0x36, 0x30, 0x2c, 0x30, 0x31, 0x2a, 0x32, 0x32, 0x0d, 0x0a };	//Set GPGGA to update every 60s
	uint8_t setGPGGA[] = {0x24, 0x50, 0x53, 0x52, 0x46, 0x31, 0x30, 0x33, 0x2c, 0x30, 0x30, 0x2c, 0x30, 0x30, 0x2c, 0x31, 0x30, 0x2c, 0x30, 0x31, 0x2a, 0x32, 0x35, 0x0d, 0x0a}; //Set GPGGA to update every 10s
	HAL_UART_Transmit(&huart1, setGPGGA, 28, HAL_MAX_DELAY);
	uint8_t setGPGSA[] = {0x24, 0x50, 0x53, 0x52, 0x46, 0x31, 0x30, 0x33, 0x2c, 0x30, 0x32, 0x2c, 0x30, 0x30, 0x2c, 0x30, 0x30, 0x2c, 0x30, 0x31, 0x2a, 0x32, 0x36, 0x0d, 0x0a}; //Disable GPGSA
	HAL_UART_Transmit(&huart1, setGPGSA, 25, HAL_MAX_DELAY);
	uint8_t setGPGSV[] = {0x24, 0x50, 0x53, 0x52, 0x46, 0x31, 0x30, 0x33, 0x2c, 0x30, 0x33, 0x2c, 0x30, 0x30, 0x2c, 0x30, 0x30, 0x2c, 0x30, 0x31, 0x2a, 0x32, 0x37, 0x0d, 0x0a}; //Disable GPGSV
	HAL_UART_Transmit(&huart1, setGPGSV, 25, HAL_MAX_DELAY);
	uint8_t setGPRMC[] = {0x24, 0x50, 0x53, 0x52, 0x46, 0x31, 0x30, 0x33, 0x2c, 0x30, 0x34, 0x2c, 0x30, 0x30, 0x2c, 0x30, 0x30, 0x2c, 0x30, 0x31, 0x2a, 0x32, 0x30, 0x0d, 0x0a}; //Disable GPRMC
	HAL_UART_Transmit(&huart1, setGPRMC, 25, HAL_MAX_DELAY);
}

/* Receiving, parsing, comparing GPS data before sending it */
void sendCoord()
{
	char buffer[128], sendbuffer[27], latitude[9], buflatitude[9], longitude[9], buflongitude[9], ns[1], ew[1], lock[1], hdop[3];
	uint8_t character[1];
	int j = 0, i = 0, internalCount = 0, commaCount = 0;

	/*
	 * Check the received character and put it in the buffer.
	 * If the character is the end of a line the NMEA command is complete.
	 */
	if (HAL_UART_Receive_IT(&huart1, character, 1) == HAL_OK)
	{
		/* Filling the buffer with the received characters */
		buffer[i - 1] = *character;

		/* When the end of a NMEA command is detected */
		if (*character == '\n')
		{
			commaCount = 0;
			internalCount = 0;

			/* Only 8 commas needed to parse the needed parts */
			for (j = 0; commaCount < 9; j++)
			{
				/* Counting Commas to determine which part we want to save. */
				if (buffer[j] == 0x2c)
				{
					commaCount++;
					j++;
				}
				switch (commaCount)
				{
				case 2:
				{	/* Get latitude */
					latitude[internalCount] = buffer[j];
					internalCount++;
					break;
				}
				case 3:
				{   /* Get North/South */
					internalCount = 0;
					ns[internalCount] = buffer[j];
					break;
				}
				case 4:
				{	/* Get longitude */
					longitude[internalCount] = buffer[j];
					internalCount++;
					break;
				}
				case 5:
				{   /* Get East/West */
					internalCount = 0;
					ew[internalCount] = buffer[j];
					break;
				}
				case 6:
				{	/* Get Lock */
					lock[internalCount] = buffer[j];
					break;
				}
				case 8:
				{	/* Get HDOP */
					hdop[internalCount] = buffer[j];
					internalCount++;
					break;
				}
				}
			}

			/* Only update the location when the received values are different form the previous one and if the GPS has a lock.*/
			if ((((strcmp(buflatitude, latitude)) != 0) || ((strcmp(buflongitude, longitude)) != 0)) && (lock[0] == '1'))
			{
				for (j = 0; j < 9; j++)
				{
					buflatitude[j] = latitude[j];
				}
				for (j = 0; j < 9; j++)
				{
					buflongitude[j] = longitude[j];
				}

				/* Merge the desired fields in 1 array. */
				for (j = 0; j < 27; j++)
				{
					if (j == 9 || j == 11 || j == 21 || j == 23)
					{
						sendbuffer[j] = 0x2c;
					} else if (j < 9)
					{
						sendbuffer[j] = latitude[j];
					} else if (j < 11)
					{
						sendbuffer[j] = ns[0];
					} else if (j < 21)
					{
						sendbuffer[j] = longitude[j - 12];
					} else if (j < 23)
					{
						sendbuffer[j] = ew[0];
					} else if (j < 27)
					{
						sendbuffer[j] = hdop[j - 24];
					}
				}
				HAL_UART_Transmit(&huart2, sendbuffer, sizeof(sendbuffer),HAL_MAX_DELAY);
				HAL_UART_Transmit(&huart2, (uint8_t*) "\n\r", sizeof("\n\r"),HAL_MAX_DELAY);
			}

			/*
			 * Usable off GPS, On Compass part designed for bigger areas
			 * The system will switch from GPS to compass when the user is back in the safe zone.
			 * THe safe zone latitude and longitude will be hardcoded in the system.
			 */
			/*if(((strcmp(latitude,latitudeMax)) > 0) || ((strcmp(latitude,latitudeMin)) < 0) || ((strcmp(longitude,longitudeMax)) > 0) || ((strcmp(longitude,longitudeMin)) < 0))
			 {
			 char latitudeMax[9] = {0x35, 0x31, 0x2E, 0x31, 0x37, 0x37, 0x36, 0x33, 0x33};
			 char latitudeMin[9] = {0x35, 0x31, 0x2E, 0x31, 0x37, 0x37, 0x36, 0x30, 0x30};
			 char longitudeMax[9] = {0x34, 0x2E, 0x34, 0x31, 0x35, 0x36, 0x38, 0x33, 0x33};
			 char longitudeMin[9] = {0x34, 0x2E, 0x34, 0x31, 0x35, 0x36, 0x38, 0x30, 0x30};

			 notEnabled = 1;
			 HAL_GPIO_WritePin(GPIOC, GPIO_PIN_7, GPIO_PIN_RESET);
			 HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_SET);
			 HAL_Delay(50);
			 HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_RESET);
			 }*/

			/* Reset buffer index */
			i = 0;
		}
		/* increase the buffer index to fill the buffer with characters */
		i = i + 1;
	}
}

/*
 * Sleep mode which will last until an interrupt is triggered. (WFI = Wait For Interrupt)
 * The regulator specifies on which regulator the sleep will happen.
 * Systick will be disabled during the sleep because it will act as an interrupt and awake the system.
 */
void enterSleep(uint32_t regulator)
{
	HAL_SuspendTick();
	__HAL_RCC_PWR_CLK_ENABLE();
	HAL_PWR_EnterSLEEPMode(regulator, PWR_SLEEPENTRY_WFI);
	HAL_ResumeTick();
}

/*
 * System Clock Configuration
 */
void SystemClock_Config(void)
{

  RCC_OscInitTypeDef RCC_OscInitStruct;
  RCC_ClkInitTypeDef RCC_ClkInitStruct;

  /* Configure the main internal regulator output voltage */
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /* Initializes the CPU, AHB and APB busses clocks */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_MSI;
  RCC_OscInitStruct.MSIState = RCC_MSI_ON;
  RCC_OscInitStruct.MSICalibrationValue = 0;
  RCC_OscInitStruct.MSIClockRange = RCC_MSIRANGE_5;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

  /* Initializes the CPU, AHB and APB busses clocks */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK|RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_MSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

  /* Configure the Systick interrupt time */
  HAL_SYSTICK_Config(HAL_RCC_GetHCLKFreq()/1000);

  /* Configure the Systick */
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

/* USART1 init function */
static void MX_USART1_UART_Init(void)
{

  huart1.Instance = USART1;
  huart1.Init.BaudRate = 4800;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
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

/* USART3 init function */
static void MX_USART3_UART_Init(void)
{

  huart3.Instance = USART3;
  huart3.Init.BaudRate = 115200;
  huart3.Init.WordLength = UART_WORDLENGTH_8B;
  huart3.Init.StopBits = UART_STOPBITS_1;
  huart3.Init.Parity = UART_PARITY_NONE;
  huart3.Init.Mode = UART_MODE_TX_RX;
  huart3.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart3.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart3) != HAL_OK)
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

  GPIO_InitTypeDef GPIO_InitStruct;

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();
  __HAL_RCC_GPIOC_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_7, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_RESET);

  /*Configure GPIO pin : PA8 (D7) Enable GPS*/
  GPIO_InitStruct.Pin = GPIO_PIN_8;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
  GPIO_InitStruct.Pull = GPIO_PULLDOWN;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pin : PC13 (User_Button)*/
  GPIO_InitStruct.Pin = GPIO_PIN_13;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pin : PC7 (D9) Power enable/disable GPS*/
  GPIO_InitStruct.Pin = GPIO_PIN_7;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pin : PB6 (D10) Enable Compass */
  GPIO_InitStruct.Pin = GPIO_PIN_6;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /* EXTI interrupt init*/
  HAL_NVIC_SetPriority(EXTI9_5_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI9_5_IRQn);
  HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);
}

/* Interrupt handler for PA8 (D7) Enable GPS*/
void EXTI9_5_IRQHandler(void)
{
	HAL_UART_Transmit(&huart2, "Entered \n\r",sizeof("Entered \n\r"), HAL_MAX_DELAY);
	notEnabled = 0;
	HAL_GPIO_WritePin(GPIOC, GPIO_PIN_7, GPIO_PIN_SET);
	__HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_8);
}

/* Interrupt handler for PC13 (User_Button)*/
void EXTI15_10_IRQHandler(void)
{
	for(int i=0; i<65535; i++);
	if(HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13))
	{
		enableCompass = 1;
	}
	__HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_13);
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/*
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

/*
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

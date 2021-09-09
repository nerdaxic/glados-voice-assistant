// GLaDOS Voice Assistant Eye controller
// Teensy 4.0 @ 600 MHz
// Nerdaxic 4.9.2021
// Credit to Mr. Volt for the original script and Aperture.h

#include <Wire.h>
#include <SPI.h>

#include "Adafruit_GFX.h"
#include "Adafruit_GC9A01A.h"
#include "Aperture.h"
#include <Adafruit_NeoPixel.h>

// Hardware pinouts
#define LED_RING_PIN 0
#define LED_REC_PIN 14
#define PIN_LED_ENABLE 7
#define TFT_DC 9 
#define TFT_CS 10
#define TFT_MOSI 11
#define TFT_SCLK 13
#define TFT_RST 8
#define TFT_MISO -1

// Should match GLaDOS eye color from Portal 2
#define GC9A01A_YELLOW 0xFEE3 

#define LED_COUNT  16
#define LOGO_HEIGHT  240
#define LOGO_WIDTH   240

// NeoPixel ring brightness, 0 (min) to 255 (max)
#define BRIGHTNESS 128

// Hardware SPI
Adafruit_GC9A01A tft(TFT_CS, TFT_DC, TFT_RST);
Adafruit_NeoPixel ring_light(LED_COUNT, LED_RING_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel rec_light(1, LED_REC_PIN, NEO_RGB + NEO_KHZ800);

// State 0 shows loading animation until 
// Raspberry Pi & glados.py have started
int state = 0;
int lastMode = NULL;

void setup() {
  // 5mm NeoPixel "REC LED"
  rec_light.begin();
  rec_light.show();

  // Display
  tft.begin(40000000);
  Serial.begin(9600);
  tft.fillScreen(GC9A01A_BLACK);
  pinMode(PIN_LED_ENABLE, OUTPUT);
  digitalWrite(PIN_LED_ENABLE, HIGH);
  tft.setRotation(0);

  // NeoPixel Ring
  ring_light.begin();
  ring_light.show();
  ring_light.setBrightness(BRIGHTNESS);
  digitalWrite(PIN_LED_ENABLE, LOW);
  pinMode(22, OUTPUT);
  digitalWrite(22, HIGH);
  
  // Show startup animation
  startAnimation();
}

void loop(void) {
  // read one byte from serial buffer and save to data_received
   if(Serial.available()) {
    char data_received = Serial.read();

    // Normal idle mode
    if(data_received == '0'){
      state = 1;
      rec_light.setPixelColor(0, rec_light.Color(5,0,0));
      rec_light.show();
      colorWipe(ring_light.gamma32(ring_light.Color(241, 203, 40)), 50);
      if(lastMode != 5){
        drawGrid(GC9A01A_YELLOW);
      }
      lastMode = 0;
    }
    
    // Yellow wait animation
    if(data_received == '1'){
      tft.fillScreen(GC9A01A_BLACK);
      colorWipe(ring_light.gamma32(ring_light.Color(241, 203, 40)), 50);
      state = 0;
      lastMode = data_received;
    }

    // Angry error
    if(data_received == '2'){
      state = 1;
      tft.fillScreen(GC9A01A_BLACK);
      colorWipe(ring_light.gamma32(ring_light.Color(128, 0, 0)), 50);
      drawGrid(GC9A01A_RED);
      rec_light.setPixelColor(0, rec_light.Color(10,0,0));
      rec_light.show();
      lastMode = data_received;
    }
    // fill white
    if(data_received == '3'){
      state = 1;
      tft.fillScreen(GC9A01A_WHITE);
      colorWipe(ring_light.gamma32(ring_light.Color(255, 255, 220)), 50);
      rec_light.setPixelColor(0, rec_light.Color(190,230,255));
      rec_light.show();
      lastMode = data_received;
    }
    // dim
    if(data_received == '4'){
      state = 1;
      tft.fillScreen(GC9A01A_BLACK);
      colorWipe(ring_light.Color(24, 15, 4), 50);
      rec_light.setPixelColor(0, rec_light.Color(0,0,0));
      rec_light.show();
      lastMode = data_received;
    }

    // Green idle mode
    if(data_received == '5'){
      rec_light.setPixelColor(0, rec_light.Color(0,20,0));
      rec_light.show();
      colorWipe(ring_light.gamma32(ring_light.Color(241, 203, 40)), 50);
      if(lastMode != 0){
        drawGrid(GC9A01A_YELLOW);
      }
      state = 1;
      lastMode = 5;
    }

    // Restart loading animation
    if(data_received == '6'){
      rec_light.setPixelColor(0, rec_light.Color(0,0,0));
      rec_light.show();
      colorWipe(ring_light.gamma32(ring_light.Color(0, 0, 0)), 50);
      tft.fillScreen(GC9A01A_BLACK);
      delay(700);
    
      startAnimation()
      
      state = 0;
      lastMode = NULL;
    }
  }

  if(state == 0){
    // Show aperture spinner until Raspberry & glados.py has started
    logoSpin(1);
  }
}

void startAnimation(){

  // Brief bright flashes
  for(int i = 0; i < 2; i++){
    rec_light.setPixelColor(0, rec_light.Color(255,0,0));
    rec_light.show();
    delay(50);
    rec_light.setPixelColor(0, rec_light.Color(0,0,0));
    rec_light.show();
    delay(700);
  }

  // Steady red light
  rec_light.setPixelColor(0, rec_light.Color(5,0,0));
  rec_light.show();

  // Dramatic effect
  delay(2000);

  // Print GLaDOS text
  tft.setCursor(16, 110);
  tft.setTextColor(GC9A01A_YELLOW);
  tft.setTextSize(3);
  tft.println("G.L.a.D.O.S.");
  delay(5000);

  // Show startup text
  tft.fillScreen(GC9A01A_BLACK);
  tft.setCursor(16, 110);
  tft.println("Startup int.");
  delay(2000);

  // Color whipe on the ring
  colorWipe(ring_light.gamma32(ring_light.Color(241, 203, 40)), 75);

  // Fill screen black
  tft.fillScreen(GC9A01A_BLACK);
}

void logoSpin(int numSpins){
  for(int ii = 0; ii < numSpins; ii++){
    tft.drawBitmap(0, 0, Aperture0, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_YELLOW);
    tft.drawBitmap(0, 0, Aperture1, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_BLACK);
    delay(50); 
    tft.drawBitmap(0, 0, Aperture0, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_YELLOW);
    tft.drawBitmap(0, 0, Aperture2, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_BLACK);
    delay(50);
    tft.drawBitmap(0, 0, Aperture0, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_YELLOW);
    tft.drawBitmap(0, 0, Aperture3, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_BLACK);
    delay(50);
    tft.drawBitmap(0, 0, Aperture0, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_YELLOW);
    tft.drawBitmap(0, 0, Aperture4, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_BLACK);
    delay(50);
    tft.drawBitmap(0, 0, Aperture0, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_YELLOW);
    tft.drawBitmap(0, 0, Aperture5, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_BLACK);
    delay(50);
    tft.drawBitmap(0, 0, Aperture0, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_YELLOW);
    tft.drawBitmap(0, 0, Aperture6, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_BLACK);
    delay(50);
    tft.drawBitmap(0, 0, Aperture0, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_YELLOW);
    tft.drawBitmap(0, 0, Aperture7, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_BLACK);
    delay(50);
    tft.drawBitmap(0, 0, Aperture0, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_YELLOW);
    tft.drawBitmap(0, 0, Aperture8, LOGO_WIDTH, LOGO_HEIGHT, GC9A01A_BLACK);
    delay(50);
  }
  
}

void colorWipe(uint32_t color, int wait) {
  for(int i=0; i<ring_light.numPixels(); i++) { // For each pixel in ring_light...
    ring_light.setPixelColor(i, color);         //  Set pixel's color (in RAM)
    ring_light.show();                          //  Update ring_light to match
    delay(wait);                           //  Pause for a moment
  }
}

// Draw the grid texture
// Approximated from GLaDOS model in the "The Lab - Robot repair" game
void drawGrid(uint16_t color){
  tft.fillScreen(GC9A01A_BLACK);
  for(int x=0; x <= 16; x++) {  
    for(int y=0; y <= 16; y++) {
      if((x== 5 && y == 1)|(x== 4 && y == 14)|(x== 14 && y == 9)){
        // Skip the 3 dots
      }
      else{
        // Draw dot in the grid
        tft.fillCircle(x*14+9, y*14+9, 6, color);
      }
    }           
  }
}

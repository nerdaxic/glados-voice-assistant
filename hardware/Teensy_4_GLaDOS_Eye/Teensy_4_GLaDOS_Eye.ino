// GLaDOS Voice Assistant Eye controller
// Teensy 4.0 @ 600 MHz
// Nerdaxic 29.8.2021
// Credit to Mr. Volt for the original script and Aperture.h

#include <Wire.h>
#include <SPI.h>

#include "Adafruit_GFX.h"
#include "Adafruit_GC9A01A.h"
#include "Aperture.h"
#include <Adafruit_NeoPixel.h>

#define LED_PIN 0
#define LED_POINT_PIN 14
#define PIN_LED_ENABLE 7
#define TFT_DC 9 
#define TFT_CS 10
#define TFT_MOSI 11
#define TFT_SCLK 13
#define TFT_RST 8
#define TFT_MISO -1
#define GC9A01A_YELLOW 0xFEE3

#define LED_COUNT  16
#define LOGO_HEIGHT  240
#define LOGO_WIDTH   240

// NeoPixel ring brightness, 0 (min) to 255 (max)
#define BRIGHTNESS 128

// Hardware SPI
Adafruit_GC9A01A tft(TFT_CS, TFT_DC, TFT_RST);
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels(1, LED_POINT_PIN, NEO_RGB + NEO_KHZ800);

// State 0 shows loading animation until Raspberry Pi & glados.py have started
int state = 0;

void setup() {
  // 5mm NeoPixel "REC LED"
  pixels.begin();
  pixels.show();

  // Display
  tft.begin(40000000);
  Serial.begin(9600);
  tft.fillScreen(GC9A01A_BLACK);
  pinMode(PIN_LED_ENABLE, OUTPUT);
  digitalWrite(PIN_LED_ENABLE, HIGH);
  tft.setRotation(0);

  // NeoPixel Ring
  strip.begin();
  strip.show();
  strip.setBrightness(BRIGHTNESS);
  digitalWrite(PIN_LED_ENABLE, LOW);
  pinMode(22, OUTPUT);
  digitalWrite(22, HIGH);
  
  // Show startup animation
  startAnimation();
}

void loop(void) {

   if(Serial.available()) {
    char data_rcvd = Serial.read();   // read one byte from serial buffer and save to data_rcvd

    // Normal idle mode
    if(data_rcvd == '0'){
      state = 1;
      pixels.setPixelColor(0, pixels.Color(10,0,0));
      pixels.show();
      tft.fillScreen(GC9A01A_BLACK);
      colorWipe(strip.gamma32(strip.Color(241, 203, 40)), 50);
      drawGrid(GC9A01A_YELLOW);
    }
    
    // Yellow wait animation
    if(data_rcvd == '1'){
      tft.fillScreen(GC9A01A_BLACK);
      colorWipe(strip.gamma32(strip.Color(241, 203, 40)), 50);
      state = 0;
    }

    // Angry error
    if(data_rcvd == '2'){
      state = 1;
      tft.fillScreen(GC9A01A_BLACK);
      colorWipe(strip.gamma32(strip.Color(128, 0, 0)), 50);
      drawGrid(GC9A01A_RED);
      pixels.setPixelColor(0, pixels.Color(10,0,0));
      pixels.show();
    }
    // fill white
    if(data_rcvd == '3'){
      state = 1;
      tft.fillScreen(GC9A01A_WHITE);
      colorWipe(strip.gamma32(strip.Color(255, 255, 220)), 50);
      pixels.setPixelColor(0, pixels.Color(190,230,255));
      pixels.show();
    }
    // dim
    if(data_rcvd == '4'){
      state = 1;
      tft.fillScreen(GC9A01A_BLACK);
      colorWipe(strip.Color(24, 15, 4), 50);
      pixels.setPixelColor(0, pixels.Color(0,0,0));
      pixels.show();
    }

    // Green idle mode
    if(data_rcvd == '5'){
      pixels.setPixelColor(0, pixels.Color(0,20,0));
      pixels.show();
      tft.fillScreen(GC9A01A_BLACK);
      colorWipe(strip.gamma32(strip.Color(241, 203, 40)), 50);
      drawGrid(GC9A01A_YELLOW);
      state = 1;
    }
  }

  if(state == 0){
    // Show aperture spinner until Raspberry has started
    logoSpin(1);
  }
}

void startAnimation(){

  // Brief bright flashes
  for(int i = 0; i < 2; i++){
    pixels.setPixelColor(0, pixels.Color(255,0,0));
    pixels.show();
    delay(50);
    pixels.setPixelColor(0, pixels.Color(0,0,0));
    pixels.show();
    delay(700);
  }

  // Steady red light
  pixels.setPixelColor(0, pixels.Color(10,0,0));
  pixels.show();

  // Dramatic effect
  delay(2000);

  // Color whipe on the ring
  colorWipe(strip.gamma32(strip.Color(241, 203, 40)), 75);
  tft.setCursor(16, 110);
  tft.setTextColor(GC9A01A_YELLOW);
  delay(1000);

  // Print GLaDOS text
  tft.setTextSize(3);
  tft.println("G.L.a.D.O.S.");
  delay(5000);

  // Show startup text
  tft.fillScreen(GC9A01A_BLACK);
  tft.setCursor(16, 110);
  tft.println("Startup int.");
  delay(2000);

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
  for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
    strip.setPixelColor(i, color);         //  Set pixel's color (in RAM)
    strip.show();                          //  Update strip to match
    delay(wait);                           //  Pause for a moment
  }
}

// Grid texture from GLaDOS model in the "Lab robot repair"
void drawGrid(uint16_t color){
  tft.fillScreen(GC9A01A_BLACK);
  for(int x=0; x <= 16; x++) {  
    for(int y=0; y <= 16; y++) {
      if((x== 5 && y == 1)|(x== 4 && y == 14)|(x== 14 && y == 9)){
        // Skip the pixel!
      }
      else{
        tft.fillCircle(x*14+9, y*14+9, 6, color);
      }
    }           
  }
}

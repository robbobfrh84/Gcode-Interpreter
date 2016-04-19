#include <SPI.h> 
#include <SD.h> 
#include <Wire.h> 
#include <Adafruit_MotorShield.h> 
#include <ShiftLCD.h> 
#include <SNESpaduino.h>

Adafruit_MotorShield AFMStop(0x61);//top motorshield. soldered to address.
Adafruit_MotorShield AFMSbot(0x60); //bottom motorshield, no soldered address.
Adafruit_StepperMotor *X = AFMSbot.getStepper(200, 1); //X-Axis, bottom motorshield, no solder address, near usb
Adafruit_StepperMotor *Z = AFMSbot.getStepper(200, 2); //Z-Axis, bottom motorshield, no solder address, far usb
Adafruit_StepperMotor *Y = AFMStop.getStepper(200, 2); //Y-Axis, Top motorshield, x0x61, near usb 
ShiftLCD lcd(8, 9, 10); // 959(Shift pin 14 to ard8, 11-9, 12-10) (8Data, 9Clock, 10Latch)
SNESpaduino pad(2,5,7); //(2 Latch yellow , 5Clock Blue, 7 Data Red) white = 5v, brown/purple ground
uint16_t btns;// address for button variables from library 16 bit, something like that.

bool bD=false;
char digit;//I think this needs to be global to read serial...
const int but1 = A3; const int but2 = A5;
long int start = 0;//TIMER: could make not global but would need to pass around a lot

void setup() {  
  Serial.begin(38400);  
  AFMSbot.begin(); AFMStop.begin(); //connect to both motorshields
  pinMode(4, OUTPUT);//SD pin
  pinMode(A1, INPUT);pinMode(A2, INPUT);pinMode(A4, INPUT);
  pinMode(3, OUTPUT);pinMode(A0, OUTPUT);pinMode(6, OUTPUT);//yellow, red, green
  pinMode(but1, INPUT); pinMode(but2, INPUT); //mounted button#1, button#2
  digitalWrite(4, HIGH);  //SD pin initalize
  digitalWrite(6, HIGH); delay(200); digitalWrite(6, LOW); //red
  digitalWrite(A0, HIGH); delay(200); digitalWrite(A0, LOW); //yellow
  digitalWrite(3, HIGH); delay(200); digitalWrite(3, LOW); //green
  lcd.begin(16, 2); // set up the LCD's number of rows and columns: 
  delay(250); Serial.println('g'); 
  if (!SD.begin(4)) { return; }  
}
//******************************** MAIN ************************************//
//******************************** LOOP ************************************//
//WARNING!!! you MUST print and end message to Chtulhlu or else send/recieve balence gets FUCKED UP!!!! OK!!!
void loop() {
  int menu = 0; String packChar; 
  if (menu == 0){ 
    digitalWrite(6, HIGH);  digitalWrite(A0, LOW); digitalWrite(3, LOW); lock(false);
    lcd.setCursor(0, 0); lcd.print("SLC>Move STR>Tmp"); lcd.setCursor(0, 1); lcd.print("[B1] > File Menu");
  }    
  if (pad.getButtons() & BTN_SELECT){ 
    menu = 1; delay(250); lock(true);
    lcd.setCursor(0, 0); lcd.print("!  LIVE  MOVE  !"); lcd.setCursor(0, 1); lcd.print("(A,B,X,Y,SL)+dir");
  }
  while (menu == 1){
    snesMove(); blinkLEDs(1000,2000);
    if (pad.getButtons() & BTN_SELECT || analogRead(but1) > 1000){ menu = 0; delay(250);}
  }
  if (analogRead(but1) > 1000){ 
    menu = 2; digitalWrite(6, LOW); digitalWrite(A0, HIGH); delay(250);
    File root = SD.open("/"); 
    while (menu == 2){
      File path =  root.openNextFile(); String fName = path.name();
      if (! path) { root.close(); delay(250);break;}
      if (path.isDirectory() || fName == "LOG.TXT") { delay(250);
      } else {
        lcd.clear();
        lcd.setCursor(0, 0); lcd.print(fName); lcd.setCursor(0, 1); lcd.print("[B2] > RUN!");
        while (true){
          if (analogRead(but1) > 1000 || (! path) || pad.getButtons() & BTN_SELECT){delay(250);break;}
          if (analogRead(but2) > 1000){
            digitalWrite(6, LOW); digitalWrite(A0, LOW); digitalWrite(3, HIGH);//RYG
            bool p = false; packChar; float rpm; float zrpm; lock(true); 
            if (path) {
              while (path.available()) {
                int c = path.read();
                if (c == 'm'){
                  while (c != '\n'){
                    c = path.read(); packChar += char(c); }
                    zrpm = ((packChar.toFloat())-.478)/.000635; packChar = String();}
                if (c == 'r'){
                  while (c != '\n'){
                    c = path.read(); packChar += char(c); }
                    rpm = ((packChar.toFloat())-.478)/.000635;  packChar = String(); }
                if (c == 'A'){ X->quickstep(FORWARD);} if (c == 'X'){ X->quickstep(BACKWARD);}
                if (c == 'Y'){ Y->quickstep(FORWARD);} if (c == 'B'){ Y->quickstep(BACKWARD);}
                if (c == 'Z'){Z->quickstep(BACKWARD);} if (c == 'C'){Z->quickstep(FORWARD);}
                delayMicroseconds(zrpm);
                if (analogRead(but1)  > 1000) { p = true;
                  digitalWrite(A0, HIGH); digitalWrite(3, LOW); 
                  delay(250); lock(false);}
                while (p == true) {  
                  if (analogRead(but1) > 1000) { 
                    digitalWrite(A0, LOW); digitalWrite(3, HIGH); 
                    lock(true); delay(250);  p = false;}
                  if (analogRead(but2) > 1000) {path.close(); root.close(); menu = 0; delay(250); break;}
                }
              }
            }
          }
        }
      }
      path.close(); 
    } 
  }  
  while (Serial.available()>0) {
    digit = Serial.read();
    if (digit == 'Q'){
      //packChar; //maybe to get rid of digit we could turn packChar into int message
      packChar += digit;
      while (digit != 'e'){//clean up by replacing digit with just Serial.read
        if (Serial.available()) { 
          digit = Serial.read();//remove global digit start here.
          packChar += digit; 
        }  
      }   
      singleMove(packChar);
    }
  }
  if (pad.getButtons() & BTN_START){
    lcd.clear(); 
    delay(250); bD= false; 
    lcd.setCursor(0, 1); lcd.print("SLC>back STR>OFF");
    while(true){
      if (pad.getButtons() & BTN_SELECT){delay(250);break;}
      if (pad.getButtons() & BTN_START && bD==false){
        lcd.setCursor(13, 1); lcd.print("ON ");lock(true);delay(250);bD=true;}
     
      if (pad.getButtons() & BTN_START && bD==true){
        lcd.setCursor(14, 1); lcd.print("FF");lock(false);delay(250);bD=false;}
      int x = analogRead(A1);  
      float v = x * 5.0;
      v /= 1024.0;
      float c = (v - 0.5) * 100;
      float f = (c * 9.0 / 5.0) + 32.0;
      int r = f;
      lcd.setCursor(0, 0); lcd.print(r);
      delay(500);
    }
  }
}  
void runTemp(){

}
void lock(bool x){
  if (x == true){
    X->step(1,FORWARD,DOUBLE); Y->step(1,FORWARD,DOUBLE);
    Z->step(1,FORWARD,DOUBLE);  Z->step(1,BACKWARD,DOUBLE);
    X->step(1,BACKWARD,DOUBLE); Y->step(1,BACKWARD,DOUBLE);
  } else { X->release(); Y->release(); Z->release();} 
}
//******************************** SD CARD / Path ************************************//
//?? create function here... less space????
//******************************** Single Move ************************************//
void singleMove(String order){  
  int c = 0; long int dist = 1; float rpm;
  while (order[c] != 'e') {
    if (order[c] == 'm'||order[c]=='r'){c=c+1; rpm=atof(&order[c]); c=c+1; rpm=(rpm-.478)/.000635;}    
    if (order[c] == 'd'){c = c + 1; dist = (atof(&order[c]))*635 ; c = c+1;} 
    c = c + 1;
  }   
  start = millis();
    for (int i=0;i<(dist-1);i++){
      if(order[c-1]=='A'){X->quickstep(FORWARD);} if(order[c-1]=='X'){X->quickstep(BACKWARD);}
      if(order[c-1]=='Y'){Y->quickstep(FORWARD);} if(order[c-1]=='B'){Y->quickstep(BACKWARD);}
      if(order[c-1]=='Z'){Z->quickstep(BACKWARD);} if(order[c-1]=='C'){Z->quickstep(FORWARD);}
      if(order[c-1]=='D'){X->quickstep(BACKWARD); Y->quickstep(FORWARD);}
      if(order[c-1]=='E'){X->quickstep(FORWARD); Y->quickstep(FORWARD);}
      if(order[c-1]=='F'){X->quickstep(FORWARD); Y->quickstep(BACKWARD);}
      if(order[c-1]=='G'){X->quickstep(BACKWARD); Y->quickstep(BACKWARD);}
      delayMicroseconds(rpm);
    }
  Serial.println(millis()-start); Serial.println('g');  
}
//******************************** SNES MOVE ************************************//  
void snesMove(){
  String dist = "0.01"; String zdist ="0.01"; 
  btns = pad.getButtons();
  if (btns & BTN_B && bD == false){ bD = true;
    lcd.setCursor(0,0); lcd.print("...Free Flow... XY:1.1 Z:2.0 s/i");
  }
  if (btns & BTN_A){delay(300);btns=pad.getButtons();}
  if (btns & BTN_X){dist="0.1"; zdist="0.10"; delay(200); btns=pad.getButtons();}
  if (btns & BTN_Y){dist="1.0"; zdist="0.25";}
  if (btns & BTN_START){dist = "4.0"; zdist="0.25" ;}
  if (btns & BTN_B || btns & BTN_A || btns & BTN_Y || btns & BTN_X || btns & BTN_START){
    if (!(btns & BTN_B)){ bD = false;
      lcd.setCursor(0,0); lcd.print("XY "+dist); lcd.write(B00100010); lcd.print(" 1.1 s/i");
      lcd.setCursor(0,1); lcd.print("Z: "+zdist); lcd.write(B00100010); lcd.print(" 2.0 s/i");
    }
    if (btns & BTN_UP) {    singleMove("Qr1.1d"+dist+"Xe");}
    if (btns & BTN_DOWN) {  singleMove("Qr1.1d"+dist+"Ae");}
    if (btns & BTN_LEFT) {  singleMove("Qr1.1d"+dist+"Ye");}
    if (btns & BTN_RIGHT) { singleMove("Qr1.1d"+dist+"Be");}
    if (btns & BTN_L) {     singleMove("Qm2.0d"+zdist+"Ze");}
    if (btns & BTN_R) {     singleMove("Qm2.0d"+zdist+"Ce");}
  } else {lcd.setCursor(0, 0); lcd.print("!  LIVE  MOVE  !"); lcd.setCursor(0, 1); lcd.print("(A,B,X,Y,SL)+dir");}
 
}  
//******************************** LED BLINK ************************************//
void blinkLEDs(int on, int off){
  if (millis()-start < on){ digitalWrite(6, HIGH); digitalWrite(A0, HIGH); digitalWrite(3, HIGH); 
  } else { digitalWrite(6, LOW); digitalWrite(A0, LOW); digitalWrite(3, LOW); }
  if (millis()-start > off){ start = millis();} 
}

//NOTES!!
//create path cut screen, time elapsed, % complete
//test smaller file. test abilty to select files.
//DonT START N E PROJECTS until temps are set up. YOURE JUST WASTING DATA!!!!!
//create new file that saves c location. that's all tanya control needs to do.Chtulhu can deal
//... with the rest. create seperate file when path is canceled. that's it. test.
//add ONE temp gage, create temp gage swap screen(select holds screen on the one that's open.
//create file to store data OPTION print to chtulhu...
//It'd be really nice to have a single step. like A+B...
// WE REALLY ONLY NEED to know the current temp. to pause and turn off. 
//maybe in the due verson do a petometer for speed control.
//fix python needs port when saving sd card. NO REASON


//<<<<<IDEAS TO TRIM CODE>>>>>
//remove btns if you can it's a special 16 varables so i don't wanna remove it from global....
//take out diagnals if it's clogged
//clean up all floats
//merge snes move and single move
// test if function of pathSD would be less space 
//what's the deal with char[] vs string. see if you can convert all...

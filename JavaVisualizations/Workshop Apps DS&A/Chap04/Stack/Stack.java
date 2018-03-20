// Stack.java
// demonstrates a stack
import java.awt.*;
import java.awt.event.*;
/////////////////////////////
class person
   {
   private int height;
   private Color color;

   public person(int h, Color c)
      { height = h; color = c; }

   public Color getColor()
      { return color; }

   public int getHeight()
      { return height; }
   }  // end class person
/////////////////////////
class personGroup
   {
   private final int appletWidth = 440;
   private final int appletHeight = 300;
   private final int topMargin = 80;     // top of cell array
   private final int leftMargin = 10;
   private final int centerX = 175;      // left stack edge
   private final int textHeight = 13;
   private final int hF1 = 12;           // fudge factors to
   private final int hF2 = 6;            // position numbers
   private final int hF3 = 0;            // within cells
   private final int vF = 8;
   private final int cellWidth = 35;
   private final int cellHeight = 17;
   private final int digits3Width = 18;
   private final int noteBoxTop = topMargin - 25;
   private final int noteBoxHeight = 25;
   private final int noteBoxWidth = 325;
   private final int ASIZE = 10;  // size of array
   private final int INIT_NUM = 4; // initial number of persons
   private final int MAX_KEY = 999;

   private person stackArray[];   // array holds stack
   private int nPersons;          // persons inserted so far
   private person tempPers;       // for insert()
   private String note;           // text displayed on screen
   private int insKey;            // key (from user) for push
   private String returnString;   // value popped or peeked
   private int codePart;          // which part of sequence?
   private int opMode;            // 1=New, 2=Fill, etc.
   private int curIn;             // current index (arrow)
   private int oldCurIn;
   private int drawMode;          // 1=one cell, 2=all cells
// ------------------
   public personGroup()           // constructor
      {
      stackArray = new person[ASIZE+1];  // extra cell for
      curIn = oldCurIn = 0;              //    curIn = 10
      nPersons = 0;                      // (arrow points to
      codePart = 1;                      // curIn-1)
      drawMode = 2;
      note = "Press any button";
      }  // end constructor
// ------------------
   // return a person of specified height and random RGB color
   public person makePerson(int height)
      {
      int red = 100 + (int)(java.lang.Math.random()*154);
      int green = 100 + (int)(java.lang.Math.random()*154);
      int blue = 100 + (int)(java.lang.Math.random()*154);
      Color newColor = new Color(red, green, blue);
      return new person(height, newColor);
      }
// ------------------
   // create a new empty array of specified size
   public void newStack()
      {
      if(opMode != 1)
         {
         opMode = 1;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            note = "Will create new, empty stack";
            drawMode = 1;
            codePart = 2;
            break;
         case 2:                             // create stack
            stackArray = new person[ASIZE];
            for(int j=0; j<ASIZE; j++)       // put null in
               stackArray[j] = null;         // all cells
            nPersons = 0;
            oldCurIn = curIn;
            curIn = 0;
            note = "New stack created";
            drawMode = 2;
            codePart = 3;
            break;
         case 3:
            note = "Press any button";
            drawMode = 1;
            codePart = 1;
            break;
         }  // end switch
      }  // end newStack()
// ------------------
   public void doFill()
      {
      int j, randVal;
      for(j=0; j<ASIZE; j++) // clear the array
         stackArray[j] = null;

      for(j=0; j<INIT_NUM; j++)
         {
         int height = (int)(java.lang.Math.random()*999);
         tempPers = makePerson(height);
         stackArray[j] = tempPers;
         }
      nPersons = INIT_NUM;
      oldCurIn = curIn;
      curIn = nPersons;
      }  // end doFill
// ------------------
   // insert a person
   public void push(boolean isNumb, int userVal)
      {
      if(opMode != 2)
         {
         opMode = 2;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            note = "Enter key of item to push";
            codePart = 2;
            break;
         case 2:
            if(!isNumb || userVal < 0 || userVal > MAX_KEY)
               {
               note="CAN'T PUSH: need key between 0 and " +
                                                      MAX_KEY;
               codePart = 1;
               }
            else if(nPersons > ASIZE-1)
               {
               note = "CAN'T PUSH: stack is full";
               codePart = 5;
               }
            else                  // can insert
               {
               insKey = userVal;
               note = "Will push item with key " + insKey;
                                  // make person to insert
               tempPers = makePerson(insKey);
               codePart = 3;
               }
            break;
         case 3:
            nPersons++;
            oldCurIn = curIn;
            curIn = nPersons;
            note = "Incremented top";
            codePart = 4;
            break;
         case 4:
            stackArray[nPersons-1] = tempPers;
            note="Inserted item with key "
                 + insKey + " at top";
            codePart = 5;
            break;
         case 5:
            note = "Press any button";
            codePart = 1;
            break;
         }  // end switch
      drawMode = 1;                 // for all code parts
      }  // end insert()
// ------------------
   public String pop()
      {
      if(opMode != 3)
         {
         opMode = 3;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            if(nPersons == 0)
               {
               note = "CAN'T POP: stack is empty";
               codePart = 4;
               }
            else
               {
               note = "Will pop item from top of stack";
               codePart = 2;
               }
            returnString = "";
            drawMode = 1;
            break;
         case 2:
            returnString = "" +
                           stackArray[nPersons-1].getHeight();
            stackArray[nPersons-1] = null;
            note = "Item removed; value returned in Number";
            drawMode = 2;  // necessary
            codePart = 3;
            break;
         case 3:
            nPersons--;
            oldCurIn = curIn;
            curIn = nPersons;
            note = "Decremented top";
            drawMode = 1;
            codePart = 4;
            break;
         case 4:
            note = "Press any button";
            drawMode = 1;
            codePart = 1;
            break;
         }  // end switch
      return returnString;
      }  // end pop()
// ------------------
   public String peek()
      {
      if(opMode != 4)
         {
         opMode = 4;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            if(nPersons == 0)
               {
               note = "CAN'T PEEK: stack is empty";
               codePart = 3;
               }
            else
               {
               note = "Will peek at item at top of stack";
               codePart = 2;
               }
            returnString = "";
            drawMode = 1;
            break;
         case 2:
            returnString = "" +
                           stackArray[nPersons-1].getHeight();
            note = "Value returned in Number";
            drawMode = 1;
            codePart = 3;
            break;
         case 3:
            note = "Press any button";
            drawMode = 1;
            codePart = 1;
            break;
         }  // end switch
      return returnString;
      }  // end peek()
// ------------------
 public void drawPerson(Graphics g, int persDex)
   {
   int x, y;
   int hF, height;

   x = centerX;
   y = appletHeight - (40 + cellHeight*persDex);

   if(persDex != 10)  // draw only arrow if curIn==10
      {
      if(persDex<10)       hF = hF1;  // fudge factors for digits
      else if(persDex<100) hF = hF2;
      else                 hF = hF3;

      g.setColor(Color.black);        // draw array index
      g.drawString(""+persDex, x + hF, y + cellHeight - vF);
      g.setColor(Color.black);        // draw rectangle
      g.drawRect(x+digits3Width+5, y-5, cellWidth, cellHeight);

      if(stackArray[persDex]==null)   // if cell not occupied,
         {
         g.setColor(Color.lightGray); // fill rectangle w/ backgnd
         g.fill3DRect(x+digits3Width+6, y-4, cellWidth-1,
                                             cellHeight-1, true);
         }
      else                            // cell is occupied
         {                            // get height and color
         height = stackArray[persDex].getHeight();
         g.setColor( stackArray[persDex].getColor() );
                                      // fill rectangle with color
         g.fill3DRect(x+digits3Width+6, y-4, cellWidth-1,
                                             cellHeight-1, true);
         if(height<10)       hF = hF1; // fudge factors for digits
         else if(height<100) hF = hF2;
         else                hF = hF3;
         g.setColor(Color.black);     // draw height number
         g.drawString(""+height, x + digits3Width + hF +15,
                                 y + cellHeight - vF);
         }  // end else(cell occupied)
      }  // end if(persDex != 10)

   if( persDex==curIn )            // draw arrow
      g.setColor(Color.red);          // for curIn, red arrow
   else                               // for all other persons,
      g.setColor(Color.lightGray);    // gray arrow
   int xTip = x + digits3Width + 8 + cellWidth;
   int yTip = y + 3*cellHeight/2 - 4;
   g.drawLine(xTip, yTip,   xTip+20, yTip);    // shaft
   g.drawLine(xTip, yTip+1, xTip+20, yTip+1);
   g.drawLine(xTip, yTip,   xTip+5,  yTip-5);  // top feather
   g.drawLine(xTip, yTip+1, xTip+5,  yTip-4);
   g.drawLine(xTip, yTip,   xTip+5,  yTip+5);  // bottom feather
   g.drawLine(xTip, yTip+1, xTip+5,  yTip+6);
   g.drawString("Top", xTip+23, yTip+5);       // "Top" of stack
   }
// ------------------
   public void draw(Graphics g)      // draw array
      {
      int j, x, y;

      if(drawMode==1)                   // draw only one person
         {
         g.setColor(Color.lightGray);   // clear text area
         g.fillRect(leftMargin, noteBoxTop, noteBoxWidth,
                    noteBoxHeight);
         g.setColor(Color.black);       // draw 'note'
         g.drawString(note, leftMargin+6,
                      noteBoxTop+textHeight+6);

         drawPerson(g, oldCurIn);       // (to erase arrow)
         drawPerson(g, curIn);          // draw current person
         drawMode = 2;
         }
      else  // drawmode==2              // draw all persons
         {
         g.setColor(Color.lightGray);   // clear entire screen
         g.fillRect(0, 0, appletWidth, appletHeight);

         g.setColor(Color.black);       // draw 'note'
         g.drawString(note, leftMargin+6,
                      noteBoxTop+textHeight+6);

         for(j=0; j<ASIZE; j++)      // draw all persons
            drawPerson(g, j);
         drawPerson(g, ASIZE);       // if curIn==10
         }  // end else(drawMode is 2)
      }  // end draw()
// ------------------
   }  // end class personGroup
////////////////////////////
public class Stack extends java.applet.Applet
                     implements Runnable, ActionListener
   {
   private Thread runner;
   private personGroup thePersonGroup;
   private int GPNumber = -1;      // general-purpose number
   private boolean isNumber = false;  // is GPNumber valid
   private TextField tf = new TextField("", 4);
   private Button newButton, pushButton, popButton, peekButton;
// ------------------
   public void init()
      {
      setLayout( new FlowLayout() );
      Panel p1 = new Panel();
      add(p1);
      p1.setLayout( new FlowLayout() );

      Panel p2 = new Panel();
      p1.add(p2);
      p2.setLayout( new FlowLayout(FlowLayout.LEFT) );

      newButton = new Button("New");       // New button
      p2.add(newButton);
      newButton.addActionListener(this);

      pushButton = new Button("Push");     // Push button
      p2.add(pushButton);
      pushButton.addActionListener(this);

      popButton = new Button("Pop");       // Pop button
      p2.add(popButton);
      popButton.addActionListener(this);

      peekButton = new Button("Peek");     // Peek button
      p2.add(peekButton);
      peekButton.addActionListener(this);

      Panel p4 = new Panel();    // text field
      p1.add(p4);
      p4.setLayout( new  FlowLayout(FlowLayout.RIGHT) );
      p4.add( new Label("Number: ") );
      p4.add(tf);
                                 // start with ASIZE cells
      thePersonGroup = new personGroup();
      thePersonGroup.doFill();   // of which INIT_NUM are filled
      repaint();
      }  // end init()
// ------------------
   public void start()
      {
      if(runner==null)
         {
         runner = new Thread(this);
         runner.start();
         }
      }
// ------------------
   public void stop()
      {
      if(runner!=null)
         {
         runner.stop();
         runner = null;
         }
      }
// ------------------
   public void paint(Graphics gg)
      { thePersonGroup.draw(gg); }
// ------------------
   public void update(Graphics gg)
      { paint(gg); }
// ------------------
   public void actionPerformed(ActionEvent event)
      {
      isNumber = true;
      String s = tf.getText();          // get the number
                                        // convert string
      try{ GPNumber = Integer.parseInt( s ); }  // to number
      catch(NumberFormatException e)
         {                              // not a number
         GPNumber = 0;
         isNumber = false;
         }
      if(event.getSource()==newButton)        // "New" button
         thePersonGroup.newStack();

      else if(event.getSource()==pushButton)  // "Push" button
         thePersonGroup.push(isNumber, GPNumber);

      else if(event.getSource()==popButton)   // "Pop" button
         {
         s = thePersonGroup.pop();    // put return value
         tf.setText(s);               // in textfield
         }

      else if(event.getSource()==peekButton)  // "Peek" button
         {
         s = thePersonGroup.peek();
         tf.setText(s);
         }

      repaint();                        // all events
      try{ Thread.sleep(10); }
      catch(InterruptedException e)
         {  }
      }  // end actionPerformed()
// ------------------
   public void run()
      {
      while(true)
         {
         }
      }  // end run()
// ------------------
   }  // end class Stack
//////////////////////////


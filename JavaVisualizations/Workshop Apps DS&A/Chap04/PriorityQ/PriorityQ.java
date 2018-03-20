// PriorityQ.java
// demonstrates priority queues
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
   private final int centerX = 175;      // left queue edge
   private final int textHeight = 13;
   private final int hF1 = 12;           // fudge factors to
   private final int hF2 = 6;            // position numbers
   private final int hF3 = 0;            // within cells
   private final int vF = 8;
   private final int cellWidth = 35;
   private final int cellHeight = 17;
   private final int blueShaft = 60;
   private final int redShaft = 15;
   private final int blackShaft = 10;
   private final int digits3Width = 18;
   private final int noteBoxTop = topMargin - 25;
   private final int noteBoxHeight = 25;
   private final int noteBoxWidth = 325;
   private final int ASIZE = 10;  // size of array
   private final int INIT_NUM = 5; // initial number of persons
   private final int MAX_KEY = 999;

   private person queArray[];   // array holds queue
   private int nPersons;          // persons inserted so far
   private person tempPers;       // for insert()
   private String note;           // text displayed on screen
   private int insKey;            // key (from user) for insert
   private String returnString;   // value removed or peeked
   private int codePart;          // which part of sequence?
   private int opMode;            // 1=New, 2=Fill, etc.
   private int front;             // front of queue (red arrow)
   private int rear;              // rear of queue (blue arrow)
   private int curIn;             // current index (black arrow)
   private int oldFront;
   private int oldCurIn;
   private int drawMode;          // 1=one cell, 2=all cells
// ------------------
   public personGroup()           // constructor
      {
      queArray = new person[ASIZE];
      front = oldFront = 0;
      rear = 0;
      curIn = oldCurIn = -9;      // invalid index for curIn
      nPersons = 0;
      codePart = 1;
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
   public void newQueue()
      {
      if(opMode != 1)
         {
         opMode = 1;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            note = "Will create new queue";
            drawMode = 1;
            codePart = 2;
            break;
         case 2:                             // create queue
            queArray = new person[ASIZE];
            nPersons = 0;
            oldFront = front;
            front = -1;
            rear = 0;
            oldCurIn = curIn;
            curIn = -9;                  // invalid index
            note = "New queue created";
            drawMode = 2;
            codePart = 3;
            break;
         case 3:
            note = "Press any button";
            drawMode = 1;
            codePart = 1;
            break;
         }  // end switch
      }  // end newQueue()
// ------------------
   public void doFill()
      {
      int height;
      for(int j=0; j<ASIZE; j++)      // clear the array
         queArray[j] = null;
      nPersons = 0;
      while(nPersons < INIT_NUM)  // fill in INIT-NUM objects
         {
         int limit = (ASIZE-nPersons) * 89;
         height = (int)(java.lang.Math.random()*limit);
         if( nPersons==0 ||
             height < queArray[nPersons-1].getHeight() )
            {
            tempPers = makePerson(height);
            queArray[nPersons++] = tempPers;
            }
         }
      rear = 0;
      front = nPersons-1;
      }  // end doFill
// ------------------
   // insert a person
   public void insert(boolean isNumb, int userVal)
      {
      if(opMode != 2)
         {
         opMode = 2;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            note = "Enter key of item to insert";
            drawMode = 1;
            codePart = 2;
            break;
         case 2:
            if(!isNumb || userVal < 0 || userVal > MAX_KEY)
               {
               note="CAN'T INSERT: need key between 0 and " +
                                                      MAX_KEY;
               codePart = 1;
               }
            else if(nPersons == ASIZE)
               {
               note = "CAN'T INSERT: queue is full";
               codePart = 5;
               }
            else                  // can insert
               {
               insKey = userVal;
               note = "Will insert item with key " + insKey;
                                  // make person to insert
               tempPers = makePerson(insKey);
               oldCurIn = curIn;
               curIn = nPersons-1;
               codePart = 3;
               }
            drawMode = 1;
            break;
         case 3:
            note = "Found insertion point";
            codePart = 4;
            if(nPersons==0 || curIn<0)
               {
               oldCurIn = curIn;
               curIn = 0;
               }
            else if( insKey <= queArray[curIn].getHeight() )
               {                                 // this the place?
               oldCurIn = curIn;
               curIn++;
               }
            else                                 // not the place
               {
               queArray[curIn+1] = queArray[curIn]; // shift up
               queArray[curIn] = null;
               oldCurIn = curIn;
               curIn--;
               note = "Shifting; searching for insertion point";
               codePart = 3;
               }
            drawMode = 1;
            break;
         case 4:
            oldFront = front;
            front++;
            nPersons++;
            queArray[curIn] = tempPers;  // insert new item
            note="Inserted item with key " + insKey;
            drawMode = 1;
            codePart = 5;
            break;
         case 5:
            note = "Press any button";
            oldCurIn = curIn;
            curIn = -9;             // turn off curIn
            drawMode = 1;
            codePart = 1;
            break;
         }  // end switch
      }  // end insert()
// ------------------
   public String remove()
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
               note = "CAN'T REMOVE: queue is empty";
               codePart = 3;
               }
            else
               {
               note = "Will remove item from front of queue";
               codePart = 2;
               }
            returnString = "";
            break;
         case 2:
            returnString = "" +
                           queArray[nPersons-1].getHeight();
            queArray[nPersons-1] = null;
            oldFront = front;
            front--;
            nPersons--;
            note = "Item removed";
            codePart = 3;
            break;
         case 3:
            note = "Press any button";
            codePart = 1;
            break;
         }  // end switch
      drawMode = 1;
      return returnString;
      }  // end remove()
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
               note = "CAN'T PEEK: queue is empty";
               codePart = 3;
               }
            else
               {
               note = "Will peek at item at front of queue";
               codePart = 2;
               }
            returnString = "";
            drawMode = 1;
            break;
         case 2:
            returnString = "" +
                           queArray[front].getHeight();
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

      if(persDex>=0 && persDex<ASIZE)    // only draw if
         {                               //    in array
         if(persDex<10)       hF = hF1;  // fudge factors
         else if(persDex<100) hF = hF2;  // for digits
         else                 hF = hF3;

         g.setColor(Color.black);        // draw array index
         g.drawString(""+persDex, x + hF, y + cellHeight - vF);
         g.setColor(Color.black);        // draw rectangle
         g.drawRect(x+digits3Width+5, y-5, cellWidth,
                                           cellHeight);
         if(queArray[persDex]==null)   // if cell not occupied,
            {
            g.setColor(Color.lightGray); // fill rect w/ backgnd
            g.fill3DRect(x+digits3Width+6, y-4, cellWidth-1,
                                             cellHeight-1, true);
            }
         else                            // cell is occupied
            {                            // get height and color
            height = queArray[persDex].getHeight();
            g.setColor( queArray[persDex].getColor() );
                                         // fill rect with color
            g.fill3DRect(x+digits3Width+6, y-4, cellWidth-1,
                                           cellHeight-1, true);
            if(height<10)       hF = hF1; // fudge for digits
            else if(height<100) hF = hF2;
            else                hF = hF3;
            g.setColor(Color.black);     // draw height number
            g.drawString(""+height, x + digits3Width + hF +15,
                                    y + cellHeight - vF);
            }  // end else(cell occupied)
         }  // end if(persDex != 10)
                                         // draw arrow, even if
      int xTip = x + digits3Width + 8 + cellWidth;  // not in
      int yTip = y + cellHeight/2 - 4;              // array

      g.setColor(Color.lightGray);       // erase old arrows
      g.drawString("Front", xTip+redShaft+3, yTip+5);
      g.drawString("Rear", xTip+blueShaft+3, yTip+5);
      drawArrow(g, blueShaft, xTip, yTip);

      if(persDex==rear)                  // if we're rear
         {
         g.setColor(Color.blue);         // blue arrow
         g.drawString("Rear", xTip+blueShaft+3, yTip+5);
         drawArrow(g, blueShaft, xTip, yTip);
         }
      if( persDex==front )               // if we're front,
         {
         g.setColor(Color.red);          // red arrow
         g.drawString("Front", xTip+redShaft+3, yTip+5);
         drawArrow(g, redShaft, xTip, yTip);
         }
      if( persDex==curIn && curIn != -9) // if we're curIn,
         {
         g.setColor(Color.black);        // black arrow
         drawArrow(g, blackShaft, xTip, yTip);
         }
      }
// ------------------
   public void drawArrow(Graphics g, int len, int xTip, int yTip)
      {
      g.drawLine(xTip, yTip,   xTip+len, yTip);    // shaft
      g.drawLine(xTip, yTip+1, xTip+len, yTip+1);
      g.drawLine(xTip, yTip,   xTip+5,   yTip-5);  // top feather
      g.drawLine(xTip, yTip+1, xTip+5,   yTip-4);
      g.drawLine(xTip, yTip,   xTip+5,   yTip+5);  // bottom feather
      g.drawLine(xTip, yTip+1, xTip+5,   yTip+6);
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

         drawPerson(g, oldFront);       // (to erase arrow)
         drawPerson(g, front);          // draw current front

         if(curIn != -9)                // if curIn being used,
            {
            drawPerson(g, curIn);       // draw it
            if(curIn < ASIZE)
               drawPerson(g, curIn+2);  // for shifting
            }
         drawPerson(g, oldCurIn);       // (to erase arrow)
         drawMode = 2;                  // for next time
         }
      else  // drawmode==2              // draw all persons
         {
         g.setColor(Color.lightGray);   // clear entire screen
         g.fillRect(0, 0, appletWidth, appletHeight);

         g.setColor(Color.black);       // draw 'note'
         g.drawString(note, leftMargin+6,
                      noteBoxTop+textHeight+6);

         for(j=0; j<ASIZE; j++)         // draw all persons
            drawPerson(g, j);
         drawPerson(g, -1);             // draw front if at -1
         }  // end else(drawMode is 2)
      }  // end draw()
// ------------------
   }  // end class personGroup
////////////////////////////
public class PriorityQ extends java.applet.Applet
                     implements Runnable, ActionListener
   {
   private Thread runner;
   private personGroup thePersonGroup;
   private int GPNumber = -1;      // general-purpose number
   private boolean isNumber = false;  // is GPNumber valid
   private TextField tf = new TextField("", 4);
   private Button newButton, insButton, remButton, peekButton;
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

      newButton = new Button("New");     // New button
      p2.add(newButton);
      newButton.addActionListener(this);

      insButton = new Button("Ins");     // Ins button
      p2.add(insButton);
      insButton.addActionListener(this);

      remButton = new Button("Rem");     // Rem button
      p2.add(remButton);
      remButton.addActionListener(this);

      peekButton = new Button("Peek");   // Peek button
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
      if(event.getSource()==newButton)       // "New" button
         thePersonGroup.newQueue();

      else if(event.getSource()==insButton)  // "Ins" button
         thePersonGroup.insert(isNumber, GPNumber);

      else if(event.getSource()==remButton)  // "Rem" button
         {
         s = thePersonGroup.remove();  // (put return value
         tf.setText(s);                //  in textfield)
         }

      else if(event.getSource()==peekButton) // "Peek" button
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
   }  // end class PriorityQ
//////////////////////////


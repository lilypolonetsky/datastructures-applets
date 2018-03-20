// Towers.java
// towers of Hanoi puzzle
import java.awt.*;
import java.awt.event.*;
///////////////////////////////////////////////////////////////
class disk
   {
   private final int groundLevel = 300; // also in tower class
   private final int height = 20;       // also in tower class

   public int width;                // width
   public Color color;              // color
   public String label;             // label (e.g. "10")
// -------------------------------------------------------------
   public disk(int w, Color c, String lab)    // constructor
      {
      width = w;
      color = c;
      label = lab;                  // 1, 2, 3, etc.
      }
// -------------------------------------------------------------
   public void drawDisk(Graphics g, int xCtr, int j)
      {
      int left = xCtr - width/2;
      int top = groundLevel - (j+1)*height;

      g.setColor(Color.black);               // black outline
      g.drawRect(left, top, width-1, height-1);
      g.drawOval(left-height/2, top, height-1, height-1);
      g.drawOval(left+width-height/2-1, top, height-1, height-1);

      g.setColor(color);                     // interior color
      g.fillRect(left+1, top+1, width-2, height-2);
      g.fillOval(left-height/2+1, top+1, height-2, height-2);
      g.fillOval(left+width-height/2, top+1, height-2, height-2);

      g.setColor(Color.black);               // disk number
      g.drawString(label, left, top+height/2+4);
      }  // end drawDisk()
// -------------------------------------------------------------
   }  // end class disk
////////////////////////////////////////////////////////////////
class tower
   {
   private final int groundLevel = 300;   // also in disk class
   private final int diskHeight = 20;     // also in disk class
   private final int maxDiskWidth = 120;  // also in gameGroup
   private final int towerWidth = 15;
   private final int towerTop = 80;
   private final int towerHeight = groundLevel - towerTop;

   public int nDisks;
   public int xCtr;
   public char label;
   public disk[] diskArray;
   public int arrayTop;
// -------------------------------------------------------------
   public tower(int x, char lab, int n)    // constructor
      {
      nDisks = n;
      xCtr = x;                     // x position of center
      label = lab;                  // A, B, C, etc.
      diskArray = new disk[nDisks];
      arrayTop = -1;
      }
// -------------------------------------------------------------
   public void insertDisk(disk d)
      {
      diskArray[++arrayTop] = d;    // push disk
      }
// -------------------------------------------------------------
   public disk removeDisk()
      {
      return diskArray[arrayTop--]; // pop disk
      }
// -------------------------------------------------------------
   public disk peekDisk()
      {
      return diskArray[arrayTop];
      }
// -------------------------------------------------------------
   public boolean isEmpty()
      {
      return arrayTop == -1;
      }
// -------------------------------------------------------------
   public boolean isFull()
      {
      return arrayTop == nDisks-1;
      }
// -------------------------------------------------------------
   public void drawTower(Graphics g, int drawMode, int ddCode)
      {
      if(drawMode==1)
         {
         if(ddCode==1)           // erase previous topmost disk
            {
            eraseDisk(g, arrayTop+1);
            return;
            }
         if(ddCode==2)           // draw topmost disk
            {
            diskArray[arrayTop].drawDisk(g, xCtr, arrayTop);
            return;
            }
         }  // end if(drawMode is 1)
      else  // drawMode is 2                  // draw everything
         {
         g.setColor(Color.black);             // black tower
         int xLeft = xCtr - towerWidth/2;
         g.fillRect(xLeft, towerTop, towerWidth, towerHeight);
         g.setColor(Color.white);             // 'A' or 'B' or 'C'
         g.drawString(""+label, xLeft+4, towerTop+15);

         for(int j=0; j<=arrayTop; j++)       // draw all disks
            {                                 // on this tower
            if(diskArray[j] != null)
               diskArray[j].drawDisk(g, xCtr, j);
            else
               break;
            }
         }  // end else(drawMode is 2)
      }  // end drawTower()
// --------------------------------------------------------------
                           // erase this tower's old topmost disk
   public void eraseDisk(Graphics g, int j)
      {
      int left = xCtr - maxDiskWidth/2 - diskHeight/2;
      int top = groundLevel - (j+1)*diskHeight;
      int width = maxDiskWidth + diskHeight;

      g.setColor(Color.lightGray);           // gray rectangle
      g.fillRect(left, top, width, diskHeight);

      g.setColor(Color.black);               // tower section
      int xLeft = xCtr - towerWidth/2;
      g.fillRect(xLeft, top, towerWidth, diskHeight);
      }  // end eraseDisk()
// -------------------------------------------------------------
   }  // end class tower
////////////////////////////////////////////////////////////////
class params     // parameters to save on stack
   {
   public int n;
   public int from;
   public int to;
   public int inter;
   public int codePart;
   public params(int nn, int f, int t, int i, int cp)
      { n=nn; from=f; to=t; inter=i; codePart=cp; }
   }  // end class params
////////////////////////////////////////////////////////////////
class stack
   {
   private int maxSize;        // size of stack array
   private params[] stackArray;
   private int top;            // top of stack
//--------------------------------------------------------------
   public stack(int s)         // constructor
      {
      maxSize = s;             // set array size
      stackArray = new params[maxSize];  // create array
      top = -1;                // no items yet
      }
//--------------------------------------------------------------
   public void push(params p)  // put item on top of stack
      {
      stackArray[++top] = p;     // increment top, insert item
      }
//--------------------------------------------------------------
   public params pop()         // take item from top of stack
      {
      return stackArray[top--];  // access item, decrement top
      }
//--------------------------------------------------------------
   public params peek()        // peek at top of stack
      {
      return stackArray[top];
      }
//--------------------------------------------------------------
   public boolean isEmpty()    // true if stack is empty
      {
      return (top == -1);
      }
//--------------------------------------------------------------
   public boolean isFull()     // true if stack is full
      {
      return (top == maxSize-1);
      }
//--------------------------------------------------------------
   }  // end class stack
////////////////////////////////////////////////////////////////
class gameGroup
   {
   private final int maxDiskWidth = 120;  // also in tower
   private final int appletWidth = 440;
   private final int appletHeight = 325;
   private final int topMargin = 70;
   private final int leftMargin = 10;
   private final int textHeight = 13;
   private final int xTowerA = 80;        // x coords of tower
   private final int xTowerB  = 220;      //    centers
   private final int xTowerC = 360;
   private final int noteBoxTop = 45;
   private final int noteBoxHeight = 25;
   private final int noteBoxWidth = appletWidth-leftMargin;
   private final int drawingBoxHeight = 229;

   private String note;         // displayed on screen
   private int opMode;          // 1=New, 2=Step, etc.
   private int codePart;        // section of code being executed
   private int drawMode;           // 1=draw two disks + msgs
                                   // 2=draw everything
   private boolean diskMoved;   // true if disk just moved
   private int ddCode;          // disk-draw code
                                   // 1=erase previous top disk
                                   // 2=draw topmost disk only
   private tower[] towerArray;  // array for 3 towers
   private int nDisks;          // total disks
   private int widthFactor;     // disk-to-disk delta
   private stack theStack;      // stack of params
   private params theseParams;  // current params;
   private int n;               // current params members
   private int from;
   private int to;
   private int inter;
   private boolean isDoneFlag;  // for Run button
// ------------------
   public gameGroup(int n)         // constructor
      {
      nDisks = n;                            // initial # disks
      widthFactor = 120/nDisks;
      towerArray = new tower[3];             // make 3 towers
      towerArray[0] = new tower(xTowerA, 'A', nDisks);
      towerArray[1] = new tower(xTowerB, 'B', nDisks);
      towerArray[2] = new tower(xTowerC, 'C', nDisks);

      for(int j=0; j<nDisks; j++)            // intall disks
         {
         int newWidth = maxDiskWidth - j*widthFactor;
                                             // random RGB color
         int red = 75+(int)(java.lang.Math.random()*180);
         int green = 75+(int)(java.lang.Math.random()*180);
         int blue = 75+(int)(java.lang.Math.random()*180);
         Color newColor = new Color(red, green, blue);
                                             // make disk
         disk theDisk = new disk(newWidth, newColor,
                                 ""+(nDisks-j));
                                             // put on tower A
         towerArray[0].insertDisk(theDisk);
         }  // end for
 //     theStack = new stack(nDisks*2);// ***need*2? ***   // make a stack
      theStack = new stack(nDisks);// ***need*2? ***   // make a stack
      note =
      "Press any button, or drag disk to another post";
      diskMoved = false;
      drawMode = 2;
      }  // end constructor
// -------------------------------------------------------------
   public void creationError()
      {
      note = "Before using New, enter number of disks (1 to 10)";
      drawMode = 1;
      }
// -------------------------------------------------------------
   public boolean isDone()
      { return isDoneFlag; }
// -------------------------------------------------------------
   public void setDone(boolean iD)
      { isDoneFlag = iD; }
// -------------------------------------------------------------
   public void startDrag(int x, int y)  // called on mouseDown()
      {
      diskMoved = false;
      from = closeTo(x, y);
      if(from==-1)
         {
         note = "DRAG the CENTER of the disk";
         return;
         }
      if( towerArray[from].isEmpty() )
         {
         note = "NO DISKS on tower " + towerArray[from].label;
         from = -1;
         return;
         }
      else
         note = "Dragging from tower " + towerArray[from].label;
      drawMode = 1;
      }  // end startDrag()
// ------------------
   public void endDrag(int x, int y)   // called on mouseUp()
      {
      diskMoved = false;
      to = closeTo(x, y);
      if(from == -1 || to == -1 || from == to)
         {
         note = "Drag a colored DISK to a different black TOWER";
         return;
         }
      note = "Dragged to tower " + towerArray[to].label;

      if( !towerArray[to].isEmpty() &&
          towerArray[from].peekDisk().width >
          towerArray[to].peekDisk().width )
         {
         note = "Must put a SMALLER disk ON a LARGER disk";
         return;
         }

      disk tempDisk= towerArray[from].removeDisk();
      towerArray[to].insertDisk(tempDisk);

      diskMoved = true;

      note = "Moved disk " + tempDisk.label + " from " +
             towerArray[from].label + " to " +
             towerArray[to].label;

      if( towerArray[2].isFull() )
         {
         note = "Congratulations! You moved all the disks!";
         return;
         }
      drawMode = 1;
      }  // end endDrag()
// -------------------------------------------------------------
   // returns 0, 1, or 2 if close to tower A, B, or C,
   // otherwise returns -1
   public int closeTo(int x, int y)
      {
      int delta = 35;
      if( java.lang.Math.abs(x - xTowerA) < delta )
         return 0;
      else if( java.lang.Math.abs(x - xTowerB) < delta )
         return 1;
      else if( java.lang.Math.abs(x - xTowerC) < delta )
         return 2;
      else return -1;
      }  // end closeTo()
// -------------------------------------------------------------
   public void step()   // step through solution
      {
      diskMoved = false;

      if(opMode != 1)
         {
         opMode = 1;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            if(towerArray[0].isEmpty() ||
               !towerArray[1].isEmpty() ||
               !towerArray[2].isEmpty() )
               {
               note="You must begin with ALL DISKS ON TOWER A";
               codePart = 1;
               }
            else
               {
               note = "Will shift all disks from A to C";
               theseParams = new params(nDisks, 0, 2, 1, 8);
               theStack.push(theseParams); // init. call to f()
               codePart = 2;               // function call
               }
            break;
         case 2:                           // function entry
            theseParams = theStack.peek();
            n = theseParams.n;
            from = theseParams.from;
            to = theseParams.to;
            inter = theseParams.inter;

            note = "Entering function with "+ n + " disks";

         //   note = "Entering function; from=" + from +
         //          "to=" + to + " inter=" + inter +
         //          "ret=" + codePart;
            codePart = 3;
            break;
         case 3:
            if(n == 1)              // only one disk left
               {
               disk tempDisk= towerArray[from].removeDisk();
               towerArray[to].insertDisk(tempDisk);
               diskMoved = true;

               note = "Moved last disk " + tempDisk.label +
                      " from " + towerArray[from].label +
                      " to " + towerArray[to].label;

               if( towerArray[2].isFull() )
                  note =
                  "Congratulations! You moved all the disks!";
               codePart = 7;        // to function exit
               }  // end if(n is 1)
            else  // n is not 1
               {
               note = "More than one disk, will continue";
               codePart = 4;        // next part of function
               }
            break;
         case 4:               // top n-1 disks from A to B
            note = "Will move top " + (n-1) + " disks from " +
                   towerArray[from].label +
                   " to " + towerArray[inter].label;
            theseParams = new params(n-1, from, inter, to, 5);
            theStack.push(theseParams);
            codePart = 2;           // function call
            break;
         case 5:              // remaining disk from A to C
            disk tempDisk= towerArray[from].removeDisk();
            towerArray[to].insertDisk(tempDisk);
            diskMoved = true;
            note = "Moved remaining disk " + n +
                   " from " + towerArray[from].label +
                   " to " + towerArray[to].label;
            codePart = 6;
            break;
         case 6:              // top n-1 disks from B to C
            note = "Will move top " + (n-1) + " disks from " +
                   towerArray[inter].label +
                   " to " + towerArray[to].label;
            theseParams = new params(n-1, inter, to, from, 7);
            theStack.push(theseParams);
            codePart = 2;              // function call
            break;
         case 7:                       // function exit
            int nOld = n;
            codePart = theseParams.codePart;
            theStack.pop();            // pop the stack
            if( !theStack.isEmpty() )
               {                       // get previous params
               theseParams = theStack.peek();
               n = theseParams.n;
               from = theseParams.from;
               to = theseParams.to;
               inter = theseParams.inter;
               }
            note = "Returning from function with " +
                   nOld + " disks";
            break;
         case 8:              // done
            note = "Press New to reset";
            isDoneFlag = true;
            codePart = 1;
            break;
         }  // end switch
      drawMode = 1;           // always drawMode = 1
      }  // end step()
// ------------------
   public void warningNew()
      {
      note = "ARE YOU SURE? Press again to reset game";
      }
//--------------------------------------------------------------
   public void draw(Graphics g)      // draw towers and disks
      {
      String s;

      if(drawMode==2)
         {
         g.setColor(Color.lightGray); // clear applet screen
         g.fillRect(0, 0, appletWidth, appletHeight);
         g.setColor(Color.black);     // draw bounding rect
         g.drawRect(2, topMargin+1, appletWidth-4,
                                         drawingBoxHeight);
         for(int j=0; j<3; j++)       // draw all three towers
            towerArray[j].drawTower(g, drawMode, 0);
         }
      else  // drawMode is 1; tell towers what to draw
         {
         for(int j=0; j<3; j++)       // draw towers
            {
            if(diskMoved && j==from)
               {
               ddCode = 1;
               towerArray[j].drawTower(g, drawMode, ddCode);
               }
            else if(diskMoved && j==to)
               {
               ddCode = 2;
               towerArray[j].drawTower(g, drawMode, ddCode);
               }
            // otherwise, don't draw tower at all
            }  // end for
         }  // end else drawMode is 1

     // display messages
     g.setColor(Color.lightGray);  // clear upper text area
     g.fillRect(leftMargin, noteBoxTop, noteBoxWidth,
                noteBoxHeight);
     g.setColor(Color.black);      // draw text ('note')
     g.drawString(note, leftMargin+6,
                  noteBoxTop+textHeight+6);
     drawMode = 2;
     }  // end draw()
//--------------------------------------------------------------
   }  // end class gameGroup
////////////////////////////////////////////////////////////////
public class Towers extends java.applet.Applet
                     implements Runnable, ActionListener,
                     MouseListener
   {
   private Thread runner;
   private gameGroup theGameGroup;
   private boolean wasClearPressed = false;
   private int GPNumber = -1;         // general-purpose number
   private boolean isNumber = false;  // is GPNumber valid?
   private int initialDisks = 4;      // initial number of disks
   private TextField tf = new TextField("", 4);
   private boolean runFlag = false;
   private Button newButton, stepButton, runButton;
// ------------------
   public void init()
      {
      addMouseListener(this);

      setLayout( new FlowLayout() );
      Panel p1 = new Panel();
      add(p1);
      p1.setLayout( new FlowLayout() );

      Panel p2 = new Panel();
      p1.add(p2);
      p2.setLayout( new FlowLayout(FlowLayout.LEFT) );

      newButton =  new Button("New");     // New Button
      p2.add(newButton);
      newButton.addActionListener(this);

      stepButton =  new Button("Step");   // Step Button
      p2.add(stepButton);
      stepButton.addActionListener(this);

      runButton =  new Button("Run");     // Run Button
      p2.add(runButton);
      runButton.addActionListener(this);

      Panel p3 = new Panel();
      p1.add(p3);
      p3.setLayout( new FlowLayout(FlowLayout.RIGHT) );
      p3.add( new Label("Enter number: ") );
      p3.add(tf);

      theGameGroup = new gameGroup(initialDisks);
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
      { theGameGroup.draw(gg); }
// ------------------
   public void update(Graphics gg)
      { paint(gg); }
// ------------------
   public void actionPerformed(ActionEvent event)
      {
      if(event.getSource() == newButton)       // "New" button?
         {
         runFlag = false;
         if(wasClearPressed)           // second press?
            {
            wasClearPressed = false;
            String s = tf.getText();   // get the number
            isNumber = true;           // to number
            try{ GPNumber = Integer.parseInt( s ); }
            catch(NumberFormatException e)
               { isNumber = false; }   // not a number
            if(isNumber==false || GPNumber>10 || GPNumber<1)
               theGameGroup.creationError();
            else
               theGameGroup = new gameGroup(GPNumber);
            }
         else                          // first press
            {
            wasClearPressed = true;
            theGameGroup.warningNew();
            }
         }
      else if(event.getSource() == stepButton) // "Step" button?
         {
         runFlag = false;
         wasClearPressed = false;
         theGameGroup.step();
         }
      else if(event.getSource()==runButton)    // "Run" button?
         {
         runFlag = true;
         wasClearPressed = false;
         theGameGroup.setDone(false);
         }
      repaint();                       // all buttons
      try{ Thread.sleep(10); }
      catch(InterruptedException e)
          {  }
      }  // end actionPerformed
//--------------------------------------------------------------
   public void run()
      {
      while(true)
         {
         if(runFlag==true)
            {
            theGameGroup.step();
            repaint();
            int delay = 100;
            try{ Thread.sleep(delay); }
            catch(InterruptedException e)
               {  }
            if( theGameGroup.isDone() )
               runFlag = false;
            }  // end if(runFlag is true)
         }  // end while
      }  // end run()
// -------------------------------------------------------------
   public void mousePressed(MouseEvent event)
      {
      int x = event.getX();
      int y = event.getY();
      wasClearPressed = false;
      if(event.getClickCount() == 1)             // single click
         theGameGroup.startDrag(x, y);
      }  // end mousePressed()
// ------------------
   public void mouseReleased(MouseEvent event)
      {
      int x = event.getX();
      int y = event.getY();
      theGameGroup.endDrag(x, y);
      repaint();
      }  // end mouseReleased()
// ------------------
   public void mouseEntered(MouseEvent e)
      {  }
// ------------------
   public void mouseExited(MouseEvent e)
      {  }
// ------------------
   public void mouseClicked(MouseEvent e)
      {  }
// ------------------
   }  // end class Towers
//////////////////////////


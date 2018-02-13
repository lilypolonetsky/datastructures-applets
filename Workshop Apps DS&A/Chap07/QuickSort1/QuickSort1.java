// QuickSort1.java
// demonstrates quick sort; uses simple pivot choice
import java.awt.*;
import java.awt.event.*;
////////////////////////////////////////////////////////////////
class stack
   {
   private int st[];
   private int top;
   stack()                   // constructor
      {
      st = new int[50];
      top = -1;
      }
   public void push(int j)   // put item on stack
      { st[++top] = j; }
   public int pop()          // take item off stack
      { return st[top--]; }
   public boolean isEmpty()  // true if nothing on stack
      { return (top == -1); }
   }
////////////////////////////////////////////////////////////////
class person
   {
   private int height;           // bar height
   private Color color;          // bar color

   public Color getColor()       // access color
      { return color; }

   public int getHeight()        // access height
      { return height; }

   public person(int h, Color c) // constructor
      {
      height = h;
      color = c;
      }
   }
////////////////////////////////////////////////////////////////
class personGroup
   {
   private final int appletWidth = 370;
   private final int appletHeight = 300;
   private final int maxHeight = 200;
   private final int topMargin = 30;
   private final int leftMargin = 10;
   private final int barLeftMargin = 35;
   private final int textHeight = 13;

   private int aSize;             // number of persons in array
   private person theArray[];     // array for holding persons
   private int barWidth;
   private int barSeparation;

   private boolean doneFlag;     // done with sort?
   private int codePart;         // code we're in (1, 2, 3)
   private int comps;            // comparisons made so far
   private int swaps;            // swaps made so far
   private int initOrder;        // 1=random, 2=backwards
   private int left;             // limits of subarray
   private int right;
   private int pivot;            // pivot point of subarray
   private int leftScan;         // indices for scanning
   private int rightScan;
   private int phonyLeft;        // cludge fixes negative range
   private stack leftStack;      // stacks for indices
   private stack rightStack;
   private String note;          // text
   private int drawMode;         // 1 = draw three bars
                                 // 2 = draw all bars
//--------------------------------------------------------------
   public personGroup(int size, int order)  // constructor
      {
      aSize = size;
      initOrder = order;
      theArray = new person[aSize];
      if(aSize==100)
         { barWidth=2; barSeparation=1; }    // many bars
      else
         { barWidth=18; barSeparation=7; }   // few bars
      comps = 0;            // no comparisons made yet
      swaps = 0;            // no swaps yet
      doneFlag = false;     // not done with sort yet
      left = 0;             // set limits to entire array
      right = aSize-1;
      pivot = right;        // pivot is rightmost element
      leftScan = left;      // set scanning indices
      rightScan = right-1;  // (leave room for pivot at right)
      codePart = 1;         // first part of outer "loop"
      leftStack = new stack();   // instantiate the stacks
      rightStack = new stack();
      Color newColor = new Color(0, 0, 0);
      note = "Press any button";
      if(initOrder==1)
         {                            // fill array with
         for(int j=0; j<aSize; j++)   //   unsorted person data
            {                         // random length
            int height = (int)(java.lang.Math.random()*195);
                                      // random RGB color
            int red = (int)(java.lang.Math.random()*254);
            int green = (int)(java.lang.Math.random()*254);
            int blue = (int)(java.lang.Math.random()*254);
            newColor = new Color(red, green, blue);
                                      // make a person
            theArray[j] = new person(height, newColor);
            }  // end for(j)
         }  // end for(initOrder)
      else                            // initOrder is 2
         {                            // fill array with
         for(int j=0; j<aSize; j++)   //   reverse-order bars
            {
            int height = 195 - (195*j)/aSize;
            int red = 255-height;
            int green = 85 * (j%3);
            int blue = height;
            newColor = new Color(red, green, blue);
                                         // make a person
            theArray[j] = new person(height, newColor);
            }  // end for(j)
         }  // end else
      drawMode = 2;
      }  // end constructor
//--------------------------------------------------------------
   public void setDrawMode(int m)
      { drawMode = m; }
//-----------------------------------------------------------
   public boolean getDone()           // get done flag
      { return doneFlag; }
//-----------------------------------------------------------
                                      // draw arrow plus text
public void arrowText(Graphics g, Color c, String s,
                      int index, int vertPos,
                      boolean showArrow, boolean showText)
   {
   int x = barLeftMargin + index*(barWidth+barSeparation);
   int y = topMargin + maxHeight + (vertPos+1)*textHeight;
   g.setColor(c);

   if(showText)
      g.drawString(s, x, y);         // draw text
   if(showArrow)
      {                              // draw arrow shaft
      g.drawLine( x+barWidth/2, topMargin+maxHeight+2,
                  x+barWidth/2, y-textHeight);
                                     // draw arrow fleches
      g.drawLine(x+barWidth/2, topMargin+maxHeight+2,
                 x+barWidth/2-3, topMargin+maxHeight+7);
      g.drawLine(x+barWidth/2, topMargin+maxHeight+2,
                 x+barWidth/2+3, topMargin+maxHeight+7);
      }  // end if
   }  // end arrowText()
//--------------------------------------------------------------
   public void drawOneBar(Graphics g, int personIndex)
      {
      if(personIndex < 0 || personIndex > aSize-1)
         return;
      int height = theArray[personIndex].getHeight();
      int x = barLeftMargin +
                  personIndex*(barWidth+barSeparation);
      int y = topMargin + maxHeight - height;
      Color c = theArray[personIndex].getColor();

      g.setColor(Color.lightGray);   // clear bar area
      g.fillRect(x, topMargin, barWidth, maxHeight);

      g.setColor(c);                 // draw bar
      g.fill3DRect(x, y, barWidth, height, true);
      if(aSize==12)
         {
         g.setColor(Color.black);    // draw index number on bar
         int xx = (personIndex > 9) ? x+2 : x+5;
         g.drawString("" + personIndex, xx,
                                        topMargin+maxHeight-2);
         }
      }
//--------------------------------------------------------------
   public void drawHorizSubArrayLine(Graphics g)
      {
      int xLeft = barLeftMargin - 2 +
                  leftScan*(barWidth+barSeparation);
      int xRight = barLeftMargin + 2 +
               (rightScan+1)*(barWidth+barSeparation) + barWidth;
      int height = theArray[pivot].getHeight();
      int yLine = topMargin + maxHeight - height;
      g.setColor(Color.black);
      g.drawLine(xLeft, yLine, xRight, yLine);
      }
//--------------------------------------------------------------
   public void draw(Graphics g)      // draw the bargraph
      {
      if(drawMode != 2)              // drawMode is 1
         {
         drawOneBar(g, leftScan);
         drawOneBar(g, rightScan);
         drawOneBar(g, pivot);
         }
      else                           // drawMode is 2
         {                           // clear applet screen
         g.setColor(Color.lightGray);
         g.fillRect(0, 0, appletWidth, appletHeight);

         for(int j=0; j<aSize; j++)  // draw all bars
            drawOneBar(g, j);
         }
      if(codePart==2)
         drawHorizSubArrayLine(g);
      g.setColor(Color.lightGray);   // clear upper text area
      g.fillRect(0, 0, 140, 6+textHeight*2);
      g.setColor(Color.black);       // display sorting data
      g.drawString("Comparisons = " + comps, leftMargin,
              2+textHeight*2);
      g.drawString("Swaps = " + swaps, leftMargin,
              2+textHeight*1);

      g.setColor(Color.lightGray);   // clear lower text area
      g.fillRect(0, topMargin+maxHeight,
                 appletWidth, textHeight*6 );

      if(aSize==12)                  // if few bars,
         {                           // display index values
                                     // and arrows
         arrowText(g, Color.red, "left",  left, 1,  true, true);
         arrowText(g, Color.red, "right", right, 1, true, true);
         arrowText(g, Color.blue, "leftScan",  leftScan, 2,
                                                    true, true);
         arrowText(g, Color.blue, "rightScan", rightScan, 3,
                                                    true, true);
         int vpos = (right-pivot < 2) ? 2 : 1;
         arrowText(g, Color.magenta, "pivot",  pivot, vpos,
                                                    true, true);
                                     // display text note
         arrowText(g, Color.black, note, 0, 4, false, true);
         }  // end if(few bars)

      else  // many bars
         {                           // display arrows, no text
         arrowText(g, Color.red, "xxx", left, 1, true, false);
         arrowText(g, Color.red, "xxx", right, 1, true, false);
         arrowText(g, Color.blue, "xxx", leftScan, 2,
                                                  true, false);
         arrowText(g, Color.blue, "xxx", rightScan, 2,
                                                  true, false);
         arrowText(g, Color.magenta, "xxx", pivot, 3,
                                                  true, false);
         }
      drawMode = 1;
      }  // end draw()
//--------------------------------------------------------------
   public void sortStep()
      {
      if(doneFlag==true)
         return;
      switch(codePart)
         {
         case 1:                  // handle small partitions
            int size = right-left+1;
            if(size <= 1)
               {
               note = "Entering quickSort(); partition ("+
               left+"-"+right+") too small to sort";
               codePart = 7;      // see if anything on stack
               }
            else
               {
               pivot = right;
               note = "Entering quickSort(); will partition ("
               +left+"-"+right+")";
               codePart = 2;
               }
            break;
         case 2:
            leftScan = left-1;     // will be left & right-1
            rightScan = right;     // before first comparison
            note = "leftScan="+leftScan+
                   ", rightScan="+rightScan+"; will scan";
            codePart = 3;
            break;
         case 3:
            // from left: find first element larger than pivot
            // (don't need leftScan<right test because of pivot)
               ++comps;
            while( theArray[++leftScan].getHeight() <
                  theArray[pivot].getHeight() )
                  ++comps;
            // from right: find first element smaller than pivot
            if(rightScan>left)
               ++comps;
            while(rightScan>left &&
                  theArray[--rightScan].getHeight() >
                  theArray[pivot].getHeight() )
               if(rightScan>left)
                  ++comps;
                               // if scans have met
            if(leftScan >= rightScan)
               {
               note =
               "Scans have met; will swap pivot and leftScan";
               codePart = 5;   // go save the pivot
               }
            else
               {
               note = "Will swap leftScan and rightScan";
               codePart = 4;   // swap the items
               }
            break;
         case 4:
            swap(leftScan, rightScan);
            note = "Will scan again";
            codePart = 3;                  // scan again
            break;
         case 5:
            swap(leftScan, pivot);         // restore pivot
            codePart = 6;
            note = "Array partitioned: left ("+
                   left+"-"+(leftScan-1)+"), right ("+
                   (leftScan+1)+"-"+right+")";
            break;
         case 6:
            leftStack.push(leftScan+1);    // save right p
            rightStack.push(right);
            note=                         // sort left partition
            "Will sort left partition ("+left+"-"+(leftScan-1)+")";
            right = leftScan-1;                // do left p
            leftScan = left;
            rightScan = right-1;
            pivot = right;
            codePart = 1;
            break;
         case 7:
            if( leftStack.isEmpty() )
               {
               doneFlag = true;          // sort is complete
               note = "Sort is complete";
               codePart = 8;
               }
            else
               {
               left = leftStack.pop();   // get saved partition
               right = rightStack.pop();
               leftScan = left;
               rightScan = right-1;
               pivot = right;
               note = "Will sort right partition ("+
                      left+"-"+right+")";
               codePart = 1;             // go back and sort it
               }
            break;
         case 8:
            codePart = 8;
            note = "Press any button";
            break;
         }  // end switch
      }  // end sortStep()
//--------------------------------------------------------------
   public void swap(int dex1, int dex2)  // swap two elements
      {
      person personHolder;
      personHolder = theArray[dex1];     // A into temp
      theArray[dex1] = theArray[dex2];   // B into A
      theArray[dex2] = personHolder;     // temp into B
      ++swaps;
      }  // end swap()
   }  // end class personGroup
////////////////////////////////////////////////////////////////
public class QuickSort1 extends java.applet.Applet
                  implements Runnable, ActionListener
   {
   private Thread runner;
   private int groupSize = 12;           // start with 12 bars
   private personGroup thePersonGroup;
   private boolean runFlag;
   private int order = 1;                // 1=random, 2=backwards
   private Button newButton, sizeButton, drawButton,
                  runButton, stepButton;
//--------------------------------------------------------------
   public void init()
      {
      thePersonGroup = new personGroup(groupSize, order);
      setLayout( new FlowLayout(FlowLayout.RIGHT) );

      newButton = new Button("New");        // New button
      add(newButton);
      newButton.addActionListener(this);

      sizeButton = new Button("Size");      // Size button
      add(sizeButton);
      sizeButton.addActionListener(this);

      drawButton = new Button("Draw");      // Draw button
      add(drawButton);
      drawButton.addActionListener(this);

      runButton = new Button("Run");        // Run button
      add(runButton);
      runButton.addActionListener(this);

      stepButton = new Button("Step");      // Step button
      add(stepButton);
      stepButton.addActionListener(this);

      runFlag = false;
      thePersonGroup.setDrawMode(2);
      // automatic repaint after init()
      }  // end init()
//--------------------------------------------------------------
   public void start()
      {
      if(runner==null)
         {
         runner = new Thread(this);
         runner.start();
         }
      }
//--------------------------------------------------------------
   public void stop()
      {
      if(runner!=null)
         {
         runner.stop();
         runner = null;
         }
      }
//--------------------------------------------------------------
   public void paint(Graphics gg)
      { thePersonGroup.draw(gg); }
//--------------------------------------------------------------
   public void update(Graphics gg)
      { paint(gg); }
//--------------------------------------------------------------
   public void actionPerformed(ActionEvent event)
      {
      if(event.getSource()==newButton)        // "New" button?
         {
         runFlag = false;
         order = (order==1) ? 2 : 1;             // toggle order
         thePersonGroup = new personGroup(groupSize, order);
         }
      else if(event.getSource()==sizeButton)  // "Size" button?
         {
         runFlag = false;
         groupSize = (groupSize==12) ? 100 : 12; // toggle size
         thePersonGroup = new personGroup(groupSize, order);
         }
      else if(event.getSource()==drawButton)  // "Draw" button?
         {
         runFlag = false;
         thePersonGroup.setDrawMode(2);
         }
      else if(event.getSource()==runButton)   // "Run" button?
         {
         thePersonGroup.setDrawMode(1);
         runFlag = true;
         }
      else if(event.getSource()==stepButton)  // "Step" button?
         {
         if(thePersonGroup.getDone()==false)
            {
            runFlag = false;
            thePersonGroup.sortStep();
            }
         }
      repaint();                        // all buttons
      }
//--------------------------------------------------------------
   public void run()
      {
      while(true)
         {
         if(runFlag==true && thePersonGroup.getDone()==false)
            {
            thePersonGroup.sortStep();
            repaint();
            thePersonGroup.setDrawMode(1);
            int delay = (groupSize==12) ? 250 : 75;
            try{ Thread.sleep(delay); }
            catch(InterruptedException e)
               {  }
            }  // end if
         }  // end while
      }  // end run()
//--------------------------------------------------------------
   }  // end class QuickSort1


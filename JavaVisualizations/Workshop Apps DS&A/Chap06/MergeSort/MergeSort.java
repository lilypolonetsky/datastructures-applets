// MergeSort.java
// demonstrates merge sort
import java.awt.*;
import java.awt.event.*;
////////////////////////////////////////////////////////////////
class params     // parameters to save on stack
   {
   public int lower;  // lower bound
   public int upper;  // upper bound
   public int mid;    // mid
   public int codePart;
   public params(int lB, int uB, int m, int cp)
      {
      lower = lB;
      upper = uB;
      mid = m;
      codePart=cp;
      }
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
      { stackArray[++top] = p; }
//--------------------------------------------------------------
   public params pop()         // take item from top of stack
      { return stackArray[top--]; }
//--------------------------------------------------------------
   public params peek()        // peek at top of stack
      { return stackArray[top]; }
//--------------------------------------------------------------
   public boolean isEmpty()    // true if stack is empty
      { return (top == -1); }
//--------------------------------------------------------------
   }  // end class stack
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

   private int aSize;            // number of persons in array
   private person theArray[];    // array for holding persons
   private person workSpace[];   // extra memory for sort
   private int barWidth;
   private int barSeparation;

 //  private boolean sortingFlag;  // are we doing a sort?
   private boolean doneFlag;     // done with sort?
   private int codePart;         // code we're in (1, 2, 3)
   private int drawMode;         // 0=draw text and arrows only
                                 // 1=draw 3 bars plus t&a
                                 // 2=draw everything
   private int oldCodePart;      // code we just left
   private int comps;            // comparisons made so far
   private int copies;           // copies made so far
   private int initOrder;        // 1=random, 2=backwards
   private String note;
   private stack theStack;
   private params theseParams;
   private int lower;
   private int upper;
   private int mid;
   private int lowPtrM;          // for "merge() routine"
   private int highPtrM;
   private int upperBoundM;
   private int lowerBoundM;
   private int jM;
   private int midM;
   private int nM;
   private boolean mergingFlag;
   //-----------------------------------------------------------
   public personGroup(int size, int order)  // constructor
      {
      aSize = size;
      initOrder = order;
      theArray = new person[aSize];
      workSpace = new person[aSize*2];
      if(aSize==100)
         { barWidth=2; barSeparation=1; }    // many bars
      else
         { barWidth=18; barSeparation=7; }   // few bars
      comps = 0;            // no comparisons made yet
      copies = 0;           // no copies yet
      doneFlag = false;     // not done with sort yet
      mergingFlag = false;  // not merging yet
      codePart = 1;         // first part of outer "loop"
      Color newColor = new Color(0, 0, 0);
      note = "Press any button";
      theStack = new stack(aSize);
      drawMode = 2;
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
      }  // end constructor
   //-----------------------------------------------------------
   public boolean getDone()           // get done flag
      { return doneFlag; }
   //-----------------------------------------------------------
   public void setDrawMode(int m)
      { drawMode = m; }
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
   //-----------------------------------------------------------
   public void drawOneBar(Graphics g, int personIndex)
      {
      if(personIndex<0 || personIndex >=aSize)
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
         int xx = (personIndex > 9) ? x : x+5;
         g.drawString("" + personIndex, xx,
                                        topMargin+maxHeight-2);
         }
      }  // end drawOneBar()
   //-----------------------------------------------------------
   public void draw(Graphics g)      // draw the bargraph
      {
      if(drawMode==2)                 // draw everything
         {
         g.setColor(Color.lightGray); // clear applet screen
         g.fillRect(0, 0, appletWidth, appletHeight);

         for(int j=0; j<aSize; j++)   // draw all bars
            drawOneBar(g, j);
         }  // end if

      else if(drawMode==1)            // draw copied bar only
         {
         drawOneBar( g, (lowerBoundM+jM-1) );
         }

      // for all modes
      g.setColor(Color.lightGray);    // clear upper text area
      g.fillRect(0, 0, 120, 6+textHeight*2);
      g.setColor(Color.black);        // display sorting data
      g.drawString("Comparisons = " + comps, leftMargin,
              2+textHeight*2);
      g.drawString("Copies = " + copies, leftMargin,
              2+textHeight*1);

      g.setColor(Color.lightGray);   // clear lower text area
      g.fillRect(0, topMargin+maxHeight,
                 appletWidth, textHeight*6 );

      if(aSize==12)                  // if few bars,
         {                           // display index values
                                     // and arrows
         arrowText(g, Color.red, "lower",  lower, 1, true, true);
         arrowText(g, Color.red, "upper", upper, 2, true, true);

         int j = lowerBoundM+jM-1;   // special "merge" arrow
         if(oldCodePart==9)
            arrowText(g, Color.magenta, "ptr",
                                   lowerBoundM, 3, true, true);
         else if(oldCodePart==10)
            arrowText(g, Color.magenta, "ptr", j, 3, true, true);
         else                        // normal "mid" arrow
            arrowText(g, Color.blue, "mid",  mid, 3, true, true);
                                     // message
         arrowText(g, Color.black, note, 0, 4, false, true);
         }  // end if(few bars)

      else  // many bars
         {                           // display arrows, no text
         arrowText(g, Color.red, "xxx", lower, 1, true, false);
         arrowText(g, Color.red, "xxx", upper, 2, true, false);
         arrowText(g, Color.blue, "xxx", mid, 3, true, false);
         }
      drawMode = 1;                 // for next time
      }  // end draw()
   //-----------------------------------------------------------
   public void sortStep() // merge sort
      {
      switch(codePart)
         {
         case 1:                     // initial call
            theseParams = new params(0, aSize-1, 0, 8);
            theStack.push(theseParams);
            note = "Initial call to mergeSort";
            drawMode = 0;
            oldCodePart = codePart;
            codePart = 2;
            break;
         case 2:                     // method entry
            theseParams = theStack.peek();
            lower = theseParams.lower;
            upper = theseParams.upper;
            note = "Entering mergeSort: "+lower+"-"+upper;
            oldCodePart = codePart;
            if(lower==upper)
               codePart = 7;        // return
            else
               codePart = 4;
            drawMode = 0;
            break;
         // no case 3
         case 4:                     // find midpoint
            mid = (lower+upper) / 2;
            note = "Will sort lower half: "+lower+"-"+mid;
                                     // call to sort lower half
            params newParams = new params(lower, mid, mid, 5);
            theStack.push(newParams);
            drawMode = 0;
            oldCodePart = codePart;
            codePart = 2;
            break;
         case 5:                     // call to sort upper half
            theseParams = theStack.peek();
            lower = theseParams.lower;
            upper = theseParams.upper;
            mid = (lower+upper) / 2;

            note = "Will sort upper half: "+(mid+1)+"-"+upper;
            params newParams2 = new params(mid+1, upper, mid, 6);
            theStack.push(newParams2);
            drawMode = 0;
            oldCodePart = codePart;
            codePart = 2;
            break;
         case 6:                     // merge arrays
            theseParams = theStack.peek();
            lower = theseParams.lower;
            upper = theseParams.upper;
            mid = (lower+upper) / 2;

            note = "Will merge ranges";
            lowPtrM = lower;         // 3 arguments to merge()
            highPtrM = mid+1;
            upperBoundM = upper;
            drawMode = 0;
            oldCodePart = codePart;
            codePart = 9;            // go to merge()
            break;
         case 7:                     // method exit
            oldCodePart = codePart;
            codePart = theseParams.codePart;  // 8, 5, or 6
            theStack.pop();
            if( !theStack.isEmpty() )
               {
               theseParams = theStack.peek();
               note = "Exiting mergeSort: "+lower+"-"+upper;
               }
            else
               note = "Exciting mergeSort; sort is complete";
            drawMode = 0;
            break;
         case 8:                     // done with sort
            doneFlag = true;
            note = "Sort is complete; Press New or Size";
            drawMode = 0;
            oldCodePart = codePart;
            codePart = 1;
            break;
         //---------------start merge()-------------------------
         case 9:                     // entry to merge()
            jM = 0;
            lowerBoundM = lowPtrM;
            midM = highPtrM -1;
            nM = upperBoundM - lowerBoundM + 1;

            note = "Merged "+lowPtrM+"-"+midM+
                   " and "+highPtrM+"-"+upperBoundM+
                   " into workspace";
                                     // array into workspace
            while(lowPtrM <= midM && highPtrM <= upperBoundM)
               {
               comps++;
               copies++;
               if(  theArray[lowPtrM].getHeight() <
                   theArray[highPtrM].getHeight() )
                  workSpace[jM++] = theArray[lowPtrM++];
               else
                  workSpace[jM++] = theArray[highPtrM++];
               }  // end while
            while(lowPtrM <= midM)          // if upper done,
               {                            // finish lower
               copies++;
               workSpace[jM++] = theArray[lowPtrM++];
               }
            while(highPtrM <= upperBoundM)  // if lower done
               {                            // finish upper
               copies++;
               workSpace[jM++] = theArray[highPtrM++];
               }
            mergingFlag = true;
            jM=0;
            oldCodePart = codePart;
            codePart = 10;
            drawMode = 0;
            break;
         case 10:                    // workspace into array
            oldCodePart = codePart;
            if(jM==nM)
               {
               note = "Merge completed";
               codePart = 7;         // return from merge()
               drawMode = 0;
               }
            else
               {
               copies++;
               theArray[lowerBoundM+jM] = workSpace[jM];
               note = "Copied workspace into "+(lowerBoundM+jM);
               jM++;
               codePart = 10;
               drawMode = 1;
               }
            break;
         //----------------end merge()--------------------------
         }  // end switch
      }  // end sortStep
   //-----------------------------------------------------------
   }  // end class personGroup
////////////////////////////////////////////////////////////////
public class MergeSort extends java.applet.Applet
                  implements Runnable, ActionListener
   {
   private Thread runner;
   private int groupSize = 12;           // start with 12 bars
   private personGroup thePersonGroup;
   private boolean runFlag;
   private int order = 1;                // 1=random, 2=backwards
   private Button newButton, sizeButton, drawButton,
                  runButton, stepButton;
   //-----------------------------------------------------------
   public void init()
      {
      thePersonGroup = new personGroup(groupSize, order);
      setLayout( new FlowLayout(FlowLayout.RIGHT) );

      newButton = new Button("New");      // New button
      add(newButton);
      newButton.addActionListener(this);

      sizeButton = new Button("Size");    // Size button
      add(sizeButton);
      sizeButton.addActionListener(this);

      drawButton = new Button("Draw");    // Draw button
      add(drawButton);
      drawButton.addActionListener(this);

      runButton = new Button("Run");      // Run button
      add(runButton);
      runButton.addActionListener(this);

      stepButton = new Button("Step");    // Step button
      add(stepButton);
      stepButton.addActionListener(this);

      thePersonGroup.setDrawMode(2);
      runFlag = false;
      // automatic repaint() after init()
      }
   //-----------------------------------------------------------
   public void start()
      {
      if(runner==null)
         {
         runner = new Thread(this);
         runner.start();
         }
      }
   //-----------------------------------------------------------
   public void stop()
      {
      if(runner!=null)
         {
         runner.stop();
         runner = null;
         }
      }
   //-----------------------------------------------------------
   public void paint(Graphics gg)
      { thePersonGroup.draw(gg); }
   //-----------------------------------------------------------
   public void update(Graphics gg)
      { paint(gg); }
   //-----------------------------------------------------------
   public void actionPerformed(ActionEvent event)
      {
      if(event.getSource() == newButton)       // "New" button?
         {
         runFlag = false;
         order = (order==1) ? 2 : 1;             // toggle order
         thePersonGroup = new personGroup(groupSize, order);
         }
      else if(event.getSource() == sizeButton) // "Size" button?
         {
         runFlag = false;
         groupSize = (groupSize==12) ? 100 : 12; // toggle size
         thePersonGroup = new personGroup(groupSize, order);
         }
      else if(event.getSource() == drawButton) // "Draw" button?
         {
         thePersonGroup.setDrawMode(2);
         }
      else if(event.getSource() == runButton)  // "Run" button?
         {
         thePersonGroup.setDrawMode(1);
         runFlag = true;
         }
      else if(event.getSource() == stepButton) // "Step" button?
         {
         if(thePersonGroup.getDone()==false)
            {
            thePersonGroup.setDrawMode(1);
            runFlag = false;
            thePersonGroup.sortStep();
            }
         }
      repaint();                        // all buttons
      }  // end actionPerformed()
   //-----------------------------------------------------------
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
   // -------------------------------------------------------------
   }  // end class MergeSort


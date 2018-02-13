// BubbleSort.java
// demonstrates selection sort
import java.awt.*;
import java.awt.event.*;
////////////////////////////////////////////////////////////////
class personBS
   {
   private int height;           // bar height
   private Color color;          // bar color

   public Color getColor()       // access color
      { return color; }

   public int getHeight()        // access height
      { return height; }

   public personBS(int h, Color c) // constructor
      {
      height = h;
      color = c;
      }
   }
////////////////////////////////////////////////////////////////
class groupBS
   {
   private final int appletWidth = 370;
   private final int appletHeight = 320;
   private final int maxHeight = 200;
   private final int topMargin = 30;
   private final int leftMargin = 10;
   private final int barLeftMargin = 35;
   private final int textHeight = 13;

   private int aSize;             // number of persons in array
   private personBS theArray[];   // array for holding persons
   private int barWidth;
   private int barSeparation;

   private int outer, inner;     // indices for sorting
   private int innerOld;         // remember previous value
   private boolean swapFlag;     // just swapped some values?
   private boolean doneFlag;     // finished a sort?
   private int comps;            // comparisons made so far
   private int swaps;            // swaps made so far
   private int initOrder;        // 1=random, 2=backwards
   Color newColor;
   private int drawMode;         // 1 = 2 bars
                                 // 2 = all bars
//--------------------------------------------------------------
   public groupBS(int size, int order)  // constructor
      {
      aSize = size;
      initOrder = order;
      theArray = new personBS[aSize];
      if(aSize==100)
         { barWidth=2; barSeparation=1; }    // many bars
      else
         { barWidth=20; barSeparation=10; }  // few bars
      outer = aSize-1;      // index initial values
      inner = 0;
      comps = 0;            // no comparisons made yet
      swaps = 0;            // no swaps made yet
      swapFlag = false;     // haven't just swapped persons
      doneFlag = false;     // not done with a sort yet
      drawMode = 2;         // draw everything
      if(initOrder==1)
         {                            // fill array with
         for(int j=0; j<aSize; j++)   //   unsorted person data
            {                         // random length
            int height = (int)(java.lang.Math.random()*199);
                                      // random RGB color
            int red = (int)(java.lang.Math.random()*254);
            int green = (int)(java.lang.Math.random()*254);
            int blue = (int)(java.lang.Math.random()*254);
            newColor = new Color(red, green, blue);
                                      // make a person
            theArray[j] = new personBS(height, newColor);
            }  // end for(j)
         }  // end for(initOrder)
      else                            // initOrder is 2
         {                            // fill array with
         for(int j=0; j<aSize; j++)   //   reverse-order bars
            {
            int height = 199 - (199*j)/aSize;
            int red = 255-height;
            int green = 85 * (j%3);
            int blue = height;
            newColor = new Color(red, green, blue);
                                      // make a person
            theArray[j] = new personBS(height, newColor);
            }  // end for(j)
         }  // end else
      }  // end constructor
//--------------------------------------------------------------
   public void setDrawMode(int m)
      { drawMode = m; }
//--------------------------------------------------------------
   public boolean getDone()
      { return doneFlag; }
//--------------------------------------------------------------
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
      int height = theArray[personIndex].getHeight();
      int x = barLeftMargin +
                  personIndex*(barWidth+barSeparation);
      int y = topMargin + maxHeight - height;
      Color c = theArray[personIndex].getColor();

      g.setColor(Color.lightGray);
      g.fillRect(x, topMargin, barWidth, maxHeight);
      g.setColor(c);
      g.fill3DRect(x, y, barWidth, height, true);
      }  // end drawOneBar()
//--------------------------------------------------------------
   public void draw(Graphics g)      // draw the bargraph
      {
      // if doing the sort, and called from run() routine,
      if(drawMode != 2)              // drawMode = 1
         {
         if(swapFlag==true)          // if bars swapped,
            {
            drawOneBar(g, innerOld);    // draw the two bars
            drawOneBar(g, innerOld+1);  //   that were swapped
            swapFlag = false;
            ++swaps;
            }
         }
      else  // drawMode is 2
         {                           // clear applet screen
         g.setColor(Color.lightGray);
         g.fillRect(0, 0, appletWidth, appletHeight);

         for(int j=0; j<aSize; j++)  // draw all bars
            drawOneBar(g, j);
         }

      g.setColor(Color.lightGray);   // clear upper text area
      g.fillRect(0, 0, 150, 6+textHeight*2);
      g.setColor(Color.black);       // display sorting data
      g.drawString("Comparisons = " + comps, leftMargin,
              2+textHeight*2);
      g.drawString("Swaps = " + swaps, leftMargin,
              2+textHeight*1);

      g.setColor(Color.lightGray);   // clear lower text area
      g.fillRect(0, topMargin+maxHeight,
                 appletWidth, textHeight*5 );

      if(aSize==10)                  // if few bars,
         {                           // display index values
                                     // and arrows
         arrowText(g, Color.red, "outer", outer, 3, true, true);
         arrowText(g, Color.blue, "inner", inner, 1, true, true);
         arrowText(g, Color.blue, "inner+1", inner+1, 1, true,
                                                           true);
         if(theArray[inner].getHeight() >
            theArray[inner+1].getHeight() )
            arrowText(g, Color.blue, "Will be swapped",
                      inner, 2, false, true);
         else
            arrowText(g, Color.blue, "Will not be swapped",
                      inner, 2, false, true);
         }  // end if(few bars)

      else  // many bars
         {                           // display arrows, no text
         arrowText(g, Color.red, "xxx", outer, 3, true, false);
         arrowText(g, Color.blue, "xxx", inner, 1, true, false);
         arrowText(g, Color.blue, "xxx", inner+1, 1, true, false);
         }
      drawMode = 1;                  // for next time
      }  // end draw()
//--------------------------------------------------------------
   public void sortStep()            // do one step in
      {                              //   sorting process
      if(doneFlag==true)
         return;
      ++comps;                       // count the comparison
                                     // compare person heights
      if( theArray[inner].getHeight() >
          theArray[inner+1].getHeight() )
         {
         swap(inner, inner+1);       // swap if appropriate
         swapFlag = true;
         }
      innerOld = inner;              // remember inner
      ++inner;                       // update indices
      if(inner > outer-1)
         {
         inner = 0;
         --outer;
         if(outer == 0)
            doneFlag = true;         // we're done
         }
      }  // end sortStep()
//--------------------------------------------------------------
   public void swap(int dex1, int dex2)  // swap two elements
      {
      personBS personHolder;
      personHolder = theArray[dex1];     // A into temp
      theArray[dex1] = theArray[dex2];   // B into A
      theArray[dex2] = personHolder;     // temp into B
      }
   }  // end class groupBS
////////////////////////////////////////////////////////////////
public class BubbleSort extends java.applet.Applet
                  implements Runnable, ActionListener
   {
   private Thread runner;
   private int groupSize = 10;         // start with 10 bars
   private groupBS thePersonGroup;
   private boolean runFlag;
   private int order = 1;              // 1=random, 2=backwards
   private Button newButton, sizeButton, drawButton, runButton,
                  stepButton;
//--------------------------------------------------------------
   public void init()
      {
      runButton = new Button("Run");
      stepButton = new Button("Step");
      runFlag = false;
      thePersonGroup = new groupBS(groupSize, order);
      setLayout( new FlowLayout(FlowLayout.RIGHT) );

      newButton = new Button("New");       // New button
      add(newButton);
      newButton.addActionListener(this);

      sizeButton = new Button("Size");     // Size button
      add(sizeButton);
      sizeButton.addActionListener(this);

      drawButton = new Button("Draw");     // Draw button
      add(drawButton);
      drawButton.addActionListener(this);

      runButton = new Button("Run");       // Run button
      add(runButton);
      runButton.addActionListener(this);

      stepButton = new Button("Step");     // Step button
      add(stepButton);
      stepButton.addActionListener(this);

      thePersonGroup.setDrawMode(2);  // these are needed
      runFlag = false;                // to prepare for
      // apparent automatic repaint after init()
      }
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
      if(event.getSource() == newButton)       // "New" button?
         {
         runFlag = false;
         order = (order==1) ? 2 :1;     // toggle order
         thePersonGroup = new groupBS(groupSize, order);
         }
      else if(event.getSource() == sizeButton) // "Size" button?
         {
         runFlag = false;
         groupSize = (groupSize==10) ? 100 : 10;
         thePersonGroup = new groupBS(groupSize, order);
         }
      else if(event.getSource() == drawButton) // "Draw" button?
         {
         runFlag = false;
         thePersonGroup.setDrawMode(2);
         }
      else if(event.getSource() == runButton)  // "Run" button?
         {
         runFlag = true;
         }
      else if(event.getSource() == stepButton) // "Step" button?
         {
         runFlag = false;
         thePersonGroup.sortStep();
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
            int delay = (groupSize==10) ? 250 : 75;
            try{ Thread.sleep(delay); }
            catch(InterruptedException e)
               {  }
            }  // end if
         }  // end while
      }  // end run()
//--------------------------------------------------------------
   }  // end class BubbleSort


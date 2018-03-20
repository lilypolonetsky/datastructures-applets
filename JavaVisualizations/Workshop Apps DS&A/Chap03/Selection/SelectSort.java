// SelectSort.java
// demonstrates selection sort
import java.awt.*;
import java.awt.event.*;
////////////////////////////////////////////////////////////////
class personSS
   {
   private int height;           // bar height
   private Color color;          // bar color

   public Color getColor()       // access color
      { return color; }

   public int getHeight()        // access height
      { return height; }

   public personSS(int h, Color c) // constructor
      {
      height = h;
      color = c;
      }
   }
////////////////////////////////////////////////////////////////
class groupSS
   {
   private final int appletWidth = 370;
   private final int appletHeight = 320;
   private final int maxHeight = 200;
   private final int topMargin = 30;
   private final int leftMargin = 10;
   private final int barLeftMargin = 35;
   private final int textHeight = 13;

   private int aSize;             // number of persons in array
   private personSS theArray[];     // array for holding persons
   private int barWidth;
   private int barSeparation;

   private int outer, inner;     // indices for sorting
   private int min;              // index of minimum value
   private int outerOld, minOld; // remember previous values
   private boolean searchFlag;   // searching for minimum?
   private boolean swapFlag;     // just swapped some values?
   private boolean doneFlag;     // done with sort?
   private int comps;            // comparisons made so far
   private int swaps;            // swaps made so far
   private int initOrder;        // 1=random, 2=backwards
   private Color newColor;
   private int drawMode;         // 1 = draw several bars
                                 // 2 = draw all bars
//--------------------------------------------------------------
   public groupSS(int size, int order)  // constructor
      {
      aSize = size;
      initOrder = order;
      theArray = new personSS[aSize];
      if(aSize==100)
         { barWidth=2; barSeparation=1; }    // many bars
      else
         { barWidth=20; barSeparation=10; }  // few bars
      outer = 0;            // index initial values
      inner = 1;
      min = 0;
      searchFlag = true;    // start by searching for minimum
      comps = 0;            // no comparisons made yet
      swaps = 0;            // no swaps made yet
      swapFlag = false;     // haven't just swapped persons
      doneFlag = false;     // not done with sort

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
            theArray[j] = new personSS(height, newColor);
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
            theArray[j] = new personSS(height, newColor);
            }  // end for(j)
         }  // end else
      drawMode = 2;
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
      }
//--------------------------------------------------------------
   public void draw(Graphics g)      // draw the bargraph
      {
      // if doing the sort, and called from run() routine,
      if(drawMode != 2)              // drawMode is 1
         {
         if(swapFlag==true)          // if bars swapped,
            {
            drawOneBar(g, outerOld); // draw the two bars
            drawOneBar(g, minOld);   //    that were swapped
            swapFlag = false;
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
                 appletWidth, textHeight*5+3 );

      if(aSize==10)                  // if few bars,
         {                           // display index values
                                     // and arrows
         arrowText(g, Color.red, "outer", outer, 1, true, true);
         arrowText(g, Color.blue, "inner", inner, 2, true, true);
         arrowText(g, Color.magenta, "min", min, 3, true, true);

         if(searchFlag==true)        // say what's happening
            arrowText(g, Color.black, "Searching for minimum",
                      0, 4, false, true);
         else
            arrowText(g, Color.black, "Will swap outer & min",
                     0, 4, false, true);
         }  // end if(few bars)

      else  // many bars
         {                           // display arrows, no text
         arrowText(g, Color.red, "xxx", outer, 1, true, false);
         arrowText(g, Color.blue, "xxx", inner, 2, true, false);
         arrowText(g, Color.magenta, "xxx", min, 3, true, false);
         }
      drawMode = 1;
      }  // end draw()
//--------------------------------------------------------------
   public void sortStep()            // do one sorting step
      {
      if(doneFlag==true)
         return;
      if(inner>aSize-1 && searchFlag==true)
         return;                     // avoid out-of-bounds
      if(searchFlag==true)           // searching for minimum
         {
         ++comps;
         if(theArray[inner].getHeight() <
            theArray[min].getHeight() )
            {
            minOld = min;
            min = inner;
            }
         ++inner;
         if(inner > aSize-1)
            searchFlag = false;      // next time, do swap
         }  // end if(searchFlag)

      else  // searchFlag==false, so we're swapping
         {
         if(min != outer)
            {
            swap(outer, min);        // swap the bars
            swapFlag = true;
            ++swaps;
            }
         outerOld = outer;           // remember old outer
         ++outer;                    // done all elements to left
         inner = outer+1;            // reset inner
         minOld = min;               // remember old minimum
         min = outer;
         searchFlag = true;          // next time, start search
         if(outer > aSize-2)
            doneFlag = true;         // we're done
         }  // end else
      }  // end sortStep()
//--------------------------------------------------------------
   public void swap(int dex1, int dex2)  // swap two elements
      {
      personSS personHolder;
      personHolder = theArray[dex1];     // A into temp
      theArray[dex1] = theArray[dex2];   // B into A
      theArray[dex2] = personHolder;     // temp into B
      }
   }  // end class groupSS
////////////////////////////////////////////////////////////////
public class SelectSort extends java.applet.Applet
                  implements Runnable, ActionListener
   {
   private Thread runner;
   private int groupSize = 10;           // start with 10 bars
   private groupSS thePersonGroup;
   private boolean runFlag;
   private int order = 1;                // 1=random, 2=backwards
   private Button newButton, sizeButton, drawButton,
                  runButton, stepButton;
//--------------------------------------------------------------
   public void init()
      {
      thePersonGroup = new groupSS(groupSize, order);
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

      runFlag = false;
      thePersonGroup.setDrawMode(2);
      // automatic repaint() after init()
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
         order = (order==1) ? 2 : 1;          // toggle order
         thePersonGroup = new groupSS(groupSize, order);
         }
      else if(event.getSource()==sizeButton)  // "Size" button?
         {
         runFlag = false;
         groupSize = (groupSize==10) ? 100 : 10; // toggle size
         thePersonGroup = new groupSS(groupSize, order);
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
         runFlag = false;
         thePersonGroup.sortStep();
         }
      repaint();                        // all buttons
      }  // end actionPerformed()
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
   }  // end class SelectSort


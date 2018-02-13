// Partition.java
// demonstrates partitioning algorithm
import java.awt.*;
import java.awt.event.*;
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
   private int oldCodePart;      // code we just left
   private int comps;            // comparisons made so far
   private int swaps;            // swaps made so far
   private int initOrder;        // 1=random, 2=backwards
   private int center;           // center of subarray
   private int pivot;            // pivot point of subarray
   private int leftScan;         // indices for scanning
   private int rightScan;
   private int partition;
   private String note;
   private int drawMode;         // 1 = draw two bars
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
      leftScan = -1;        // 0 (afer ++) set scanning indices
      rightScan = aSize;    // aSize-1 (after --)
      codePart = 1;         // first part of outer "loop"
      Color newColor = new Color(0, 0, 0);
      note = "Press any button";
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
//--------------------------------------------------------------
   public boolean getDone()           // get done flag
      { return doneFlag; }
//--------------------------------------------------------------                                      // draw arrow plus text
   public void arrowText(Graphics g, Color c, String s,
                         int index, int vertPos,
                         boolean showArrow, boolean showText)
      {
      if(index < 0 || index > aSize-1)
         return;
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
      if(personIndex<0 || personIndex> aSize-1)
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
      }
//--------------------------------------------------------------
   public void draw(Graphics g)      // draw the bargraph
      {
      if(drawMode != 2)              // drawMode is 1
         {
         drawOneBar(g, leftScan);
         drawOneBar(g, rightScan);
         }
      else                           // drawMode is 2
         {                           // clear applet screen
         g.setColor(Color.lightGray);
         g.fillRect(0, 0, appletWidth, appletHeight);

         for(int j=0; j<aSize; j++)  // draw all bars
            drawOneBar(g, j);
         }
      g.setColor(Color.black);       // draw horiz line
      int y = topMargin + maxHeight - pivot;
      g.drawLine(leftMargin-5, y, appletWidth-2*leftMargin, y);

      g.setColor(Color.lightGray);   // clear upper text area
      g.fillRect(0, 0, 120, 6+textHeight*2);
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
         if(oldCodePart==7 || oldCodePart==8)
            arrowText(g, Color.magenta, "partition", partition,
                                                 1, true, true);
         else
            {
            arrowText(g, Color.blue, "leftScan",  leftScan, 2,
                                                    true, true);
            arrowText(g, Color.blue, "rightScan", rightScan, 3,
                                                    true, true);
            }
                                     // display note
         arrowText(g, Color.black, note, 0, 4, false, true);
         }  // end if(few bars)

      else  // many bars
         {                           // display arrows, no text
         if(oldCodePart==7 || oldCodePart==8)
            arrowText(g, Color.magenta, "xxx", partition, 3,
                                                  true, false);
         else
            {
            arrowText(g, Color.blue, "xxx", leftScan, 2,
                                                  true, false);
            arrowText(g, Color.blue, "xxx", rightScan, 2,
                                                  true, false);
            }
         }  // end else many bars
      drawMode = 1;
      }  // end draw()
//--------------------------------------------------------------
   public void partStep()
      {
      if(doneFlag==true)
         return;
      switch(codePart)
         {
         case 1:
            pivot = 70 + (int)(java.lang.Math.random()*60);

            note = "Pivot value is " + pivot;
            oldCodePart = codePart;
            codePart = 3;
            break;
         // no case 2
         case 3:
            note = "Will scan from left";
            oldCodePart = codePart;
            codePart = 4;
            break;
         case 4:
            oldCodePart = codePart;
            ++comps;
            if( theArray[++leftScan].getHeight() < pivot )
               {
               note = "Continuing left scan";
               codePart = 4;
               }
            else if(leftScan >= rightScan)
               {
               note = "Scans have met";
               codePart = 7;
               }
            else
               {
               note = "Will scan from right";
               codePart = 5;
               }
            break;
         case 5:
            oldCodePart = codePart;
            ++comps;
            if( theArray[--rightScan].getHeight() > pivot )
               {
               note = "Continuing right scan";
               codePart = 5;
               }
            else if(leftScan >= rightScan)
               {
               note = "Scans have met";
               codePart = 7;
               }
            else
               {
               note = "Will swap leftScan and rightScan";
               codePart = 6;
               }
            break;
         case 6:
            swap(leftScan, rightScan);
            note = "Will scan again from left";
            oldCodePart = codePart;
            codePart = 4;
            break;
         case 7:
            partition = leftScan;
            note = "Arrow shows partition";
            oldCodePart = codePart;
            codePart = 8;
            break;
         case 8:
            doneFlag = true;
            leftScan = 0;
            rightScan = aSize-1;
            note = "Press New to reset";
            oldCodePart = codePart;
            codePart = 1;
            break;
         }  // end switch
      }  // end partStep()
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
public class Partition extends java.applet.Applet
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
         runFlag = false;
         thePersonGroup.setDrawMode(2);
         }
      else if(event.getSource() == runButton)  // "Run" button?
         {
         runFlag = true;
         thePersonGroup.setDrawMode(1);
         }
      else if(event.getSource() == stepButton) // "Step" button?
         {
         if(thePersonGroup.getDone()==false)
            {
            runFlag = false;
            thePersonGroup.partStep();
            }
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
            thePersonGroup.partStep();
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
   }  // end class Partition


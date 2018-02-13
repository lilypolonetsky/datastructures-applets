// InsertSort.java
// demonstrates insertion sort
import java.awt.*;
import java.awt.event.*;
////////////////////////////////////////////////////////////////
class personIS
   {
   private int height;           // bar height
   private Color color;          // bar color

   public Color getColor()       // access color
      { return color; }

   public int getHeight()        // access height
      { return height; }

   public personIS(int h, Color c) // constructor
      {
      height = h;
      color = c;
      }
   }  // end class personIS
////////////////////////////////////////////////////////////////
class groupIS
   {
   private final int appletWidth = 370;
   private final int appletHeight = 320;
   private final int maxHeight = 200;
   private final int topMargin = 30;
   private final int leftMargin = 10;
   private final int barLeftMargin = 35;
   private final int textHeight = 13;

   private int aSize;             // number of persons in array
   private personIS theArray[];   // array for holding persons
   private int barWidth;
   private int barSeparation;

   private int outer, inner;     // indices for sorting
   private int outerOld, innerOld; // remember previous values
   private boolean doneFlag;     // done with sort?
   private int codePart;         // code we're in (1, 2, 3)
   private int comps;            // comparisons made so far
   private int copies;           // copies made so far
   private int initOrder;        // 1=random, 2=backwards
   private Color newColor;
   private int drawMode;         // 1 = draw several bars
                                 // 2 = draw all bars
//--------------------------------------------------------------
   public groupIS(int size, int order)  // constructor
      {
      aSize = size;
      initOrder = order;
      theArray = new personIS[aSize+2];  // (two extra places)
      if(aSize==100)
         { barWidth=2; barSeparation=1; }    // many bars
      else
         { barWidth=18; barSeparation=7; }   // few bars
      inner = outer = 1;    // index initial values
      innerOld = outerOld = 1;
      comps = 0;            // no comparisons made yet
      copies = 0;           // no copies made yet
      doneFlag = false;     // not done with sort yet
      codePart = 1;         // first part of outer "loop"
      Color newColor = new Color(0, 0, 0);
      if(initOrder==1)
         {                            // fill array with
         for(int j=0; j<aSize; j++)   //   unsorted person data
            {                         // random length
            int height = 10+(int)(java.lang.Math.random()*189);
                                      // random RGB color
            int red = (int)(java.lang.Math.random()*254);
            int green = (int)(java.lang.Math.random()*254);
            int blue = (int)(java.lang.Math.random()*254);
            newColor = new Color(red, green, blue);
                                      // make a person
            theArray[j] = new personIS(height, newColor);
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
            theArray[j] = new personIS(height, newColor);
            }  // end for(j)
         }  // end else
                                      // blank bar
      theArray[aSize] = new personIS(0, Color.lightGray);
                                      // temp (person holder)
      theArray[aSize+1] = new personIS(0, Color.lightGray);
      drawMode = 2;
      }  // end constructor
//--------------------------------------------------------------
   public void setDrawMode(int m)
      { drawMode = m; }
//--------------------------------------------------------------
   public boolean getDone()           // get done flag
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
      g.fillRect( x, topMargin, barWidth, maxHeight);
      g.setColor(c);
      g.fill3DRect(x, y, barWidth, height, true);
      }
//--------------------------------------------------------------
   public void draw(Graphics g)      // draw the bargraph
      {
      // if doing the sort, and called from run() routine,
      if(drawMode != 2)
         {
         switch(codePart)             // drawMode is 1
            {
            case 1:
               drawOneBar(g, inner);  // draw inner bar
               break;
            case 2:
               drawOneBar(g, aSize+1);    // temp bar
               drawOneBar(g, innerOld);
               break;
            case 3:
               drawOneBar(g, inner);      // draw inner bar
               break;
            }  // end switch
         }  // end if
      else                           // drawMode is 2
         {                           // clear applet screen
         g.setColor(Color.lightGray);
         g.fillRect(0, 0, appletWidth, appletHeight);

         for(int j=0; j<aSize; j++)  // draw all bars
            drawOneBar(g, j);
         drawOneBar(g, aSize+1);     // draw temp bar
         }

      g.setColor(Color.lightGray);   // clear upper text area
      g.fillRect(0, 0, 135, 6+textHeight*2);
      g.setColor(Color.black);       // display sorting data
      g.drawString("Comparisons = " + comps, leftMargin,
              2+textHeight*2);
      g.drawString("Copies = " + copies, leftMargin,
              2+textHeight*1);

      g.setColor(Color.lightGray);   // clear lower text area
      g.fillRect(0, topMargin+maxHeight,
                 appletWidth, textHeight*6 );

      if(aSize==10)                  // if few bars,
         {                           // display index values
                                     // and arrows
         arrowText(g, Color.red, "outer", outer, 1, true, true);
         arrowText(g, Color.blue, "inner", inner, 2, true, true);
         arrowText(g, Color.magenta, "temp", aSize+1, 1, true,
                                                           true);
         switch(codePart)
            {
            case 1:
               arrowText(g, Color.black,
                         "Will copy outer to temp",
                         0, 3, false, true);
               break;
            case 2:
               if(inner>0)
                  arrowText(g, Color.black,
                            "Have compared inner-1 and temp",
                            0, 3, false, true);
               else
                  arrowText(g, Color.black,
                            "Now inner is 0, so",
                            0, 3, false, true);

               if(inner>0 &&
                       theArray[inner-1].getHeight() >=
                              theArray[aSize+1].getHeight() )
                  arrowText(g, Color.black,
                            "   Will copy inner-1 to inner",
                            0, 4, false, true);
               else
                  arrowText(g, Color.black,
                            "   No copy necessary",
                            0, 4, false, true);
               break;
            case 3:
               arrowText(g, Color.black,
                         "Will copy temp to inner",
                         0, 3, false, true);
               break;
            }  // end switch
         }  // end if(few bars)
      else  // many bars
         {                           // display arrows, no text
         arrowText(g, Color.red, "xxx", outer, 1, true, false);
         arrowText(g, Color.blue, "xxx", inner, 2, true, false);
         arrowText(g, Color.magenta, "xxx", aSize+1, 3, true,
                                                         false);
         }
      drawMode = 1;                  // for next time
      }  // end draw()
//--------------------------------------------------------------
   public void sortStep()            // do one sorting step
      {
      // theArray[aSize+1] is used as a temporary personIS store
      switch(codePart)               // which part of code?
         {
         case 1:                     // first part of outer loop
            theArray[aSize+1] = theArray[outer];  // copy to temp
            ++copies;
            innerOld = inner;
            inner = outer;
            codePart = 2;            // next time: inner
            break;
         case 2:                     // inner loop
            ++comps;
            if(inner>0 &&
                    theArray[inner-1].getHeight() >=
                           theArray[aSize+1].getHeight() )
               {
               theArray[inner] = theArray[inner-1];
               ++copies;
               innerOld = inner;
               --inner;
               }
            else                     // done inner loop
               codePart = 3;         // next time: last outer
            break;
         case 3:                     // last part, outer loop
            theArray[inner] = theArray[aSize+1];  // from temp
            ++copies;
            outerOld = outer;
            ++outer;
            if(outer==aSize)         // finished the sort?
               doneFlag = true;
            codePart = 1;            // next time: first outer
            break;
         }  // end switch
      }  // end sortStep()
   }  // end class groupIS
////////////////////////////////////////////////////////////////
public class InsertSort extends java.applet.Applet
                  implements Runnable, ActionListener
   {
   private Thread runner;
   private int groupSize = 10;           // start with 10 bars
   private groupIS thePersonGroup;
   private boolean runFlag;
   private int order = 1;                // 1=random, 2=backwards
   private Button newButton, sizeButton, drawButton,
                  runButton, stepButton;
//--------------------------------------------------------------
   public void init()
      {
      runFlag = false;
      thePersonGroup = new groupIS(groupSize, order);
      setLayout( new FlowLayout(FlowLayout.RIGHT) );

      newButton = new Button("New");
      add(newButton);
      newButton.addActionListener(this);

      sizeButton = new Button("Size");
      add(sizeButton);
      sizeButton.addActionListener(this);

      drawButton = new Button("Draw");
      add(drawButton);
      drawButton.addActionListener(this);

      runButton = new Button("Run");
      add(runButton);
      runButton.addActionListener(this);

      stepButton = new Button("Step");
      add(stepButton);
      stepButton.addActionListener(this);

      thePersonGroup.setDrawMode(2);
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
         thePersonGroup = new groupIS(groupSize, order);
         }
      else if(event.getSource()==sizeButton)  // "Size" button?
         {
         runFlag = false;
         groupSize = (groupSize==10) ? 100 : 10; // toggle size
         thePersonGroup = new groupIS(groupSize, order);
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
   }  // end class InsertSort


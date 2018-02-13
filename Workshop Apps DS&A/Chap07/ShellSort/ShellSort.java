// shellSort.java
// demonstrates shell sort
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
   private final int appletHeight = 320;
   private final int maxHeight = 200;
   private final int topMargin = 30;
   private final int leftMargin = 10;
   private final int barLeftMargin = 35;
   private final int textHeight = 13;

   private int aSize;             // number of persons in array
   private person theArray[];     // array for holding persons
   private int barWidth;
   private int barSeparation;

   private int Outer, Inner;     // indices for sorting
   private int outerOld, innerOld; // remember previous values
   private int h;                // interval for shell sort
   private boolean doneFlag;     // done with sort?
   private int codePart;         // code we're in (1, 2, 3)
   private int comps;            // comparisons made so far
   private int copies;           // copies made so far
   private int initOrder;        // 1=random, 2=backwards
   private String note;          // displayed text note
   private int drawMode;         // 1 = draw 3 bars
                                 // 2 = draw all bars
//--------------------------------------------------------------
   public personGroup(int size, int order)  // constructor
      {
      aSize = size;
      initOrder = order;
      theArray = new person[aSize+2];  // (two extra places)
      if(aSize==100)
         { barWidth=2; barSeparation=1; }    // many bars
      else
         { barWidth=18; barSeparation=7; }   // few bars
      h = 1;                // calculate initial value of h
      while(h <= aSize/3)
         h = h*3 + 1;       // (1, 4, 13, 40, 121, ...)
      Inner = Outer = h;
      innerOld = outerOld = h;
      comps = 0;            // no comparisons made yet
      copies = 0;           // no copies made yet
      doneFlag = false;     // not done with sort yet
      note = "Press any button";
      codePart = 1;         // first part of outer "loop"
      Color newColor = new Color(0, 0, 0);
      if(initOrder==1)
         {                            // fill array with
         for(int j=0; j<aSize; j++)   //   unsorted person data
            {                         // random length
            int height = 20+(int)(java.lang.Math.random()*175);
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
            int height = 20 + 175 - (175*j)/aSize;
            int red = 255-height;
            int green = 85 * (j%3);
            int blue = height;
            newColor = new Color(red, green, blue);
                                         // make a person
            theArray[j] = new person(height, newColor);
            }  // end for(j)
         }  // end else
                                      // two "dummy" persons
      theArray[aSize] = new person(0, newColor);
      theArray[aSize+1] = new person(0, newColor);
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
   public void drawOneBar(Graphics g, int persDex)
      {
      if(persDex < 0 || persDex > aSize+1)
         return;
      int height = theArray[persDex].getHeight();
      if(height < 5)
         return;
      int x = barLeftMargin +
                   persDex*(barWidth+barSeparation);
      int y = topMargin + maxHeight - height;
      Color c = theArray[persDex].getColor();

      g.setColor(Color.lightGray);
      g.fillRect(x, topMargin, barWidth, maxHeight);
      g.setColor(c);
      g.fill3DRect(x, y, barWidth, height, true);
      }
//--------------------------------------------------------------
   public void draw(Graphics g)      // draw the bargraph
      {
      if(drawMode != 2)              // drawMode is 1
         {
         switch(codePart)
            {
            case 3:
            case 6:
               drawOneBar(g, aSize+1);    // temp bar
               drawOneBar(g, innerOld);
               drawOneBar(g, Inner);
               break;
            case 2:
            case 5:
               drawOneBar(g, innerOld);
               drawOneBar(g, Inner);
               break;
            }  // end switch
         }  // end if
      else                           // drawMode is 2, so
         {                           // clear applet screen
         g.setColor(Color.lightGray);
         g.fillRect(0, 0, appletWidth, appletHeight);

         for(int j=0; j<aSize; j++)  // draw all bars
            drawOneBar(g, j);
         drawOneBar(g, aSize+1);     // draw temp bar
                                     // draw temp text
         arrowText(g, Color.magenta, "xxx", aSize+1, 3, true,
                                                         false);
         }

      g.setColor(Color.lightGray);   // clear upper text area
      g.fillRect(0, 0, 120, 6+textHeight*2);
      g.setColor(Color.black);       // display sorting data
      g.drawString("Comparisons = " + comps, leftMargin,
              2+textHeight*2);
      g.drawString("Copies = " + copies, leftMargin,
              2+textHeight*1);

      g.setColor(Color.lightGray);   // clear lower text area
      g.fillRect(0, topMargin+maxHeight,
                 appletWidth, textHeight*6 );
                                     // display value of h
      arrowText(g, Color.black, "h="+h, 8, 5,  false, true);

      if(aSize==10)                  // if few bars,
         {                           // display index values
                                     // and arrows
         arrowText(g, Color.red, "outer",  Outer, 1, true, true);
         arrowText(g, Color.blue, "inner", Inner, 2, true, true);
         if(Inner-h >= 0)
            arrowText(g, Color.blue, "inner-h", Inner-h, 3,
                                                     true, true);
         arrowText(g, Color.magenta, "temp", aSize+1, 1,
                                                     true, true);
                                     // display note text
         arrowText(g, Color.black, note, 0, 4, false, true);
         }  // end if(few bars)

      else  // many bars
         {                           // display arrows, no text
         arrowText(g, Color.red, "xxx", Outer, 1, true, false);
         arrowText(g, Color.blue, "xxx", Inner, 2, true, false);
         arrowText(g, Color.blue, "xxx", Inner-h, 2, true,
                                                         false);
         }
      drawMode = 1;
      }  // end draw()
//--------------------------------------------------------------
   public void sortStep()            // do one sorting step
      {
      if(doneFlag==true)
         return;
      // theArray[aSize+1] is used as the temporary person store
      switch(codePart)               // which part of code?
         {
         case 1:                     // entry for given h
            note =
            ""+h+"-sorting array; will copy outer to temp";
            codePart = 2;
            break;
         case 2:                     // copy outer to temp
            ++copies;
            theArray[aSize+1] = theArray[Outer];
            innerOld = Inner;
            Inner = Outer;
            if(Inner > h-1)
               note = "Will compare inner-h and temp";
            else
               note = "There is no inner-h";
            codePart = 3;
            break;
         case 3:                     // compare inner-h and temp
            if(Inner > h-1)
               {
               ++comps;
               if( theArray[Inner-h].getHeight() >=
                            theArray[aSize+1].getHeight() )
                  {
                  note =
                  "inner-h >= temp; will copy inner-h to inner";
                  codePart = 4;
                  }
               else
                  {
                  note =
                  "inner-h < temp; will copy temp to inner";
                  codePart = 5;
                  }
               }  // end if(Inner...)
            else
               {
               note = "Will copy temp to inner";
               codePart = 5;
               }
            break;
          case 4:                    // copy inner-h to inner
            theArray[Inner] = theArray[Inner-h];
            ++copies;
            innerOld = Inner;
            Inner -= h;
            if(Inner > h-1)
               note = "Will compare inner-h and temp";
            else
               note = "There is no inner-h";
            codePart = 3;
            break;
         case 5:                     // copy temp to inner
            theArray[Inner] = theArray[aSize+1];
            ++copies;

            outerOld = Outer;        // check outer
            ++Outer;
            if(Outer < aSize)        // if not done interval,
               {
               note = "Will copy outer to temp";
               codePart = 2;         // keep moving outer
               }
            else                     // n-sort is done
               {
               h = (h-1) / 3;        // new interval size
               if(h>0)               // if 1 or greater,
                  {
                  Inner = Outer = h;    // reset indices
                  note =
                  ""+h+"-sorting array. Will copy outer to temp";
                  codePart = 2;         // sort again with new h
                  }
               else                     // otherwise,
                  {
                  note = "Shell sort is complete";
                  codePart = 6;
                  }
               }  // end else n-sort is done
            break;
         case 6:
            doneFlag = true;            // sort is complete
            note = "Press New or Size to reset";
            codePart = 6;
            break;
         }  // end switch
      }  // end sortStep()
//--------------------------------------------------------------
   }  // end class personGroup
////////////////////////////////////////////////////////////////
public class ShellSort extends java.applet.Applet
                  implements Runnable, ActionListener
   {
   private Thread runner;
   private int groupSize = 10;           // start with 10 bars
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
         groupSize = (groupSize==10) ? 100 : 10;  // toggle size
         thePersonGroup = new personGroup(groupSize, order);
         }
      else if(event.getSource() == drawButton) // "Draw" button?
         {
         runFlag = false;
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
   }  // end class ShellSort


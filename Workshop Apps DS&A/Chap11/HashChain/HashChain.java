// HashChain.java
// demonstrates hash tables with chaining
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
class link
   {
   public person persData;

   public link(person pd)
      { persData = pd; }
   }
/////////////////////////
class bucket
   {
   public link linkArray[];
   public static final int MAX_LINKS = 6;
   public int nLinks;        // number of links being used

   public bucket()
      {
      linkArray = new link[MAX_LINKS];
      nLinks = 0;
      }
   }
/////////////////////////
class personGroup
   {
   private final int appletWidth = 440;
   private final int appletHeight = 320;
   private final int topMargin = 70;     // top of cell table
   private final int leftMargin = 10;
   private final int textHeight = 13;
   private final int hF1 = 12;           // fudge factors to
   private final int hF2 = 6;            // position numbers
   private final int hF3 = 0;            // within cells
   private final int vF = 8;
   private final int columnWidth = 60;
   private final int cellWidth = 35;
   private final int arrowLen = columnWidth - cellWidth - 3;
   private final int cellHeight = 17;
   private final int digits3Width = 18;
   private final int rowHeight = cellHeight + 7;
   private final int noteBoxTop = topMargin - 25;
   private final int noteBoxHeight = 25;
   private final int noteBoxWidth = 320;
   private final int MAX_BUCKETS = 1000; // max size bucket table
   private final int MAX_KEY = 999;
   private final int linesInView = 10;   // buckets displayed

   private bucket bucketArray[];  // array holds linked lists
   private int totalBuckets;      // current number of lists
   private int nPersons;          // persons inserted so far
   private person tempPers;       // for insert()
   private String note;           // text displayed on screen
   private int fillValue;         // value from user for fill
   private int insKey;            // key from user for insert
   private int findKey;           // key from user for find
   private int delKey;            // key from user for delete
   private int codePart;          // which part of sequence?
   private int codePart2;         //    for fill
   private int opMode;            // 1=Fill, 2=Ins, etc.
   private int curList;           // current list
   private int curLink;           // current link in a list
   private int oldCurList;
   private int oldCurLink;
   private int drawMode;          // 1 = one person, 2 = all pers
   private int topDisplayLine;    // bucket at top of display
// ------------------
   public personGroup(int bucks)           // constructor
      {
      totalBuckets = bucks;
      bucketArray = new bucket[totalBuckets];
      for(int j=0; j<totalBuckets; j++)
         bucketArray[j] = new bucket();
      curList = oldCurList = 0;
      nPersons = 0;
      codePart = 1;
      codePart2 = 1;
      drawMode = 2;
      topDisplayLine = 0;
      }  // end constructor
// ------------------
   public void setScrollValue(int scrollValue)
      {
      topDisplayLine = scrollValue;
      drawMode = 2;
      }
// ------------------
   public int getScrollValue()
      { return topDisplayLine; }
// ------------------
   public int getScrollRange()
   //   { return totalBuckets - linesInView; }
      { return totalBuckets; }
// ------------------
   public int getLinesInView()
      { return linesInView; }
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
   // create a new array bucket objects
   public void newArray(boolean isNumb, int userVal)
      {
      if(opMode != 1)
         {
         opMode = 1;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            note = "Enter number of linked lists in array: ";
            drawMode = 1;
            codePart = 2;
            oldCurList = curList;
            curList = 0;
            oldCurLink = curLink;
            curLink = 0;
            break;
         case 2:
            if(!isNumb || userVal < 0 || userVal > MAX_BUCKETS)
               {
               note = "ERROR: use size between 0 and " +
                                                   MAX_BUCKETS;
               codePart = 1;      // inappropriate size
               }
            else
               {
               totalBuckets = userVal;
               note = "Will create empty table with " +
                       totalBuckets + " lists";
               codePart = 4;
               }
            drawMode = 1;
            break;
         // no case 3
         case 4:
            bucketArray = new bucket[totalBuckets];
            for(int j=0; j<totalBuckets; j++)  // empty bucket
               bucketArray[j] = new bucket();  // in all cells
            nPersons = 0;
            topDisplayLine = 0;
            note = "New table created; total items = " +
                                                   nPersons;
            drawMode = 2;
            codePart = 6;
            break;
         case 5:
            oldCurList = curList;
            curList = 0;
            drawMode = 1;
            codePart = 6;
            break;
         case 6:
            note = "Press any button";
            drawMode = 1;
            codePart = 1;
            break;
         }  // end switch
      }  // end newArray()
// ------------------
   public void fill(boolean isNumb, int userVal)
      {
      if(opMode != 2)
         {
         opMode = 2;
         codePart2 = 1;
         }
      switch(codePart2)
         {
         case 1:
            note = "Enter number of items to fill in";
            drawMode = 1;
            codePart2 = 2;
            break;
         case 2:
            int maxPersons = totalBuckets*bucket.MAX_LINKS;
            if(isNumb != true || userVal<0 || userVal>maxPersons)
               {
               note = "ERROR: can't fill more than "
                                   + maxPersons + " items";
               drawMode = 1;
               codePart2 = 1;
               }
            else
               {                        // clear table of lists
               for(int j=0; j<totalBuckets; j++)
                  bucketArray[j] = new bucket();
               fillValue = userVal;
               note = "Will fill in " + fillValue + " items";
               drawMode = 2;
               codePart2 = 3;
               }
            break;
         case 3:
            nPersons = 0;
            doFill(fillValue);
            opMode = 2;
            note = "Fill completed; total items = " + nPersons;
            oldCurList = curList;
            curList = 0;
            drawMode = 3;
            codePart2 = 4;
            break;
         case 4:
            note = "Press any button";
            drawMode = 1;
            codePart2 = 1;
            break;
         }  // end switch
      }  // end fill
// ------------------
   public void doFill(int totalPersons)
      {
      int j, randVal;
      oldCurList = curList;
      curList = 0;
      codePart = 1;
      while(nPersons < totalPersons)
         {
         insert(true, -1);      // codePart: 1
         randVal = (int)(java.lang.Math.random()*MAX_KEY);
         insert(true, randVal); // codePart: 2
         while(codePart != 1)
            insert( true, -1);  // 3, 3, 3, ... 3, 5, 6, 1
         }
      topDisplayLine = 0;
      }  // end doFill
// ------------------
   // insert a person
   public void insert(boolean isNumb, int userVal)
      {
      int dupDex;
      if(opMode != 3)
         {
         opMode = 3;
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
            else
               {
               insKey = userVal;
                                  // make person to insert
               tempPers = makePerson(insKey);
               note = "Will insert item with key " + insKey;
               codePart = 3;
               }
            drawMode = 1;
            break;
         case 3:
            oldCurList = curList;
            curList = hashFunction(insKey); // get hash value
            topDisplayLine = curList;        // (for scroll)
            oldCurLink = curLink;
            curLink = 0;
            note = "Will insert in list " + curList;
            drawMode = 1;
            codePart = 4;
            break;
         case 4:
            if(bucketArray[curList].nLinks == bucket.MAX_LINKS)
               {
               note = "CAN'T INSERT: list " + curList +
                      " is full";
               drawMode = 1;
               codePart = 6;
               }
            else
               {                        // shift list right
               for(int j=bucketArray[curList].nLinks; j>0; j--)
                  bucketArray[curList].linkArray[j] =
                          bucketArray[curList].linkArray[j-1];
                                        // insert in list
               bucketArray[curList].linkArray[0] =
                                            new link(tempPers);
               bucketArray[curList].nLinks++;
               nPersons++;
               note="Inserted item with key " + insKey +
                    " in list " + curList;
               drawMode = 2;
               codePart = 5;
               }
            break;
         case 5:
            note = "Insertion completed; total items = "
                                               + nPersons;
            drawMode = 1;
            codePart = 6;
            break;
         case 6:
            oldCurList = curList;
            curList = 0;
            topDisplayLine = 0;
            note = "Press any button";
            drawMode = 1;
            codePart = 1;
            break;
         }  // end switch
      }  // end insert()
// ------------------
   public void find(boolean isNumb, int userVal)
      {
      if(opMode != 4)
         {
         opMode = 4;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            note = "Enter key of item to find";
            codePart = 2;
            break;
         case 2:
            if(!isNumb || userVal < 0 || userVal > MAX_KEY)
               {
               note="CAN'T FIND: use key between 0 and "+MAX_KEY;
               codePart = 1;
               }
            else
               {
               findKey = userVal;
               note="Will try to find item with key "+findKey;
               codePart = 3;
               }
            break;
         case 3:
            oldCurList = curList;
            curList = hashFunction(findKey); // get hash value
            topDisplayLine = curList;        // (for scroll)
            oldCurLink = curLink;
            curLink = 0;
            note = "Item with key " + findKey +
                   " should be in list " + curList;
            codePart = 4;
            break;
         case 4:
            if(bucketArray[curList].nLinks == 0)
               {                            // no links
               note = "Can't find item with key " + findKey;
               codePart = 6;
               }
            else if(bucketArray[curList].linkArray[curLink].
                                 persData.getHeight() == findKey)
               {                            // match
               note="Have found item with key " + findKey;
               codePart = 6;
               }
            else if(curLink == bucketArray[curList].nLinks - 1)
               {                            // last link
               note = "Can't find item with key " + findKey;
               codePart = 6;
               }
            else
               {
               oldCurList = curList;        // (necessary)
               oldCurLink = curLink;        // go to next link
               curLink++;
               note = "Looking for item with key " + findKey
                      + " at link " + curLink;
               codePart = 4;
               }
            break;
         // no case 5
         case 6:
            oldCurList = curList;
            curList = 0;
            oldCurLink = curLink;
            curLink = 0;
            topDisplayLine = 0;
            note = "Press any button";
            codePart = 1;
            break;
         }  // end switch
      drawMode = 1;             // no changes during find
      }  // end find()
// ------------------
   public void delete(boolean isNumb, int userVal)
      {
      if(opMode != 5)
         {
         opMode = 5;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            note = "Enter key of item to delete";
            drawMode = 1;
            codePart = 2;
            break;
         case 2:
            if(!isNumb || userVal < 0 || userVal > MAX_KEY)
               {
               note="CAN'T FIND: use key between 0 and "+MAX_KEY;
               codePart = 1;
               }
            else
               {
               delKey = userVal;
               note="Will try to delete item with key "+delKey;
               codePart = 3;
               }
            drawMode = 1;
            break;
         case 3:
            oldCurList = curList;
            curList = hashFunction(delKey); // get hash value
            topDisplayLine = curList;       // (for scroll)
            oldCurLink = curLink;
            curLink = 0;
            note = "Item with key " + delKey +
                   " should be in list " + curList;
            drawMode = 1;
            codePart = 4;
            break;
         case 4:
            if(bucketArray[curList].nLinks == 0)
               {                            // no links
               note = "Can't find item with key " + delKey;
               codePart = 6;
               }
            else if(bucketArray[curList].linkArray[curLink].
                                 persData.getHeight() == delKey)
               {                            // match
               note="Have found item with key " + delKey;
               codePart = 5;
               }
            else if(curLink == bucketArray[curList].nLinks - 1)
               {                            // last link
               note = "Can't find item with key " + delKey;
               codePart = 6;
               }
            else
               {
               oldCurList = curList;        // (necessary)
               oldCurLink = curLink;        // go to next link
               curLink++;
               note = "Looking for item with key " + delKey
                      + " at link " + curLink;
               codePart = 4;
               }
            drawMode = 1;
            break;
         case 5:                            // delete it
            bucketArray[curList].linkArray[curLink] = null;
            int n = bucketArray[curList].nLinks;     // shift
            for(int j=curLink; j<n-1; j++)           // other
               bucketArray[curList].linkArray[j] =   // links
                       bucketArray[curList].linkArray[j+1];
            bucketArray[curList].nLinks--;
        //    oldCurList = curList;           // (necessary)
            oldCurLink = curLink;
            curLink = curLink>0 ? curLink-- : 0;
            note="Deleted item with key " + delKey;
            drawMode = 2;
            codePart = 6;
            break;
         case 6:
            topDisplayLine = 0;
            oldCurList = curList;
            curList = 0;
            oldCurLink = curLink;
            curLink = 0;
            note = "Press any button";
            drawMode = 2;
            codePart = 1;
            break;
         }  // end switch
      }  // end delete()
// ------------------
   // returns index resulting from hashing person's height
   public int hashFunction(int key)
      {
      return key % totalBuckets;
      }
// ------------------
 public void drawLink(Graphics g, int listDex, int linkDex )
   {
   int x, y;
   int hF, height;

   x = leftMargin + columnWidth * linkDex;
   y = topMargin + 9 + rowHeight * (listDex-topDisplayLine);

   if(listDex<10)       hF = hF1;  // fudge factors for digits
   else if(listDex<100) hF = hF2;
   else                 hF = hF3;

   if(linkDex==0 && drawMode==2)
      {
      g.setColor(Color.black);     // draw array index
      g.drawString(""+listDex, x + hF, y + cellHeight - vF);
      }
   g.setColor(Color.black);        // draw rectangle
   g.drawRect(x+digits3Width+5, y-5, cellWidth, cellHeight);
                                   // if cell not occupied,
   if(bucketArray[listDex].linkArray[linkDex]==null)
      {
      if(linkDex==0)               // if first in list,
         {                         // fill rectangle w/ backgnd
         g.setColor(Color.lightGray);
         g.fill3DRect(x+digits3Width+6, y-4, cellWidth-1,
                                          cellHeight-1, true);
         }
      }
   else                            // cell is occupied
      {                            // get height and color
      height = bucketArray[listDex].
                    linkArray[linkDex].persData.getHeight();
      g.setColor( bucketArray[listDex].
                    linkArray[linkDex].persData.getColor() );
                                   // fill rectangle with color
      g.fill3DRect(x+digits3Width+6, y-4, cellWidth-1,
                                          cellHeight-1, true);
      if(height<10)       hF = hF1; // fudge factors for digits
      else if(height<100) hF = hF2;
      else                hF = hF3;
      g.setColor(Color.black);     // draw height number
      g.drawString(""+height, x + digits3Width + hF +15,
                              y + cellHeight - vF);
      if(linkDex != 0)             // except for 1st link,
         {                         // draw arrow on left
         int xTip = x+arrowLen-1;
         int yTip = y+cellHeight/2-4;
         g.drawLine(xTip, yTip, xTip-arrowLen, yTip);
         g.drawLine(xTip, yTip, xTip-7, yTip-4);
         g.drawLine(xTip, yTip, xTip-7, yTip+4);
         }
      }
                                     // draw arrow
   if(listDex==curList && linkDex==curLink)
      g.setColor(Color.red);         // current cell, red arrow
   else                              // all other cells,
      g.setColor(Color.lightGray);   // gray arrow

   int xTip = x + digits3Width + 8 + cellWidth;
   int yTip = y-2;
   g.drawLine(xTip,   yTip,   xTip+16, yTip-10); // shaft
   g.drawLine(xTip,   yTip+1, xTip+16, yTip-9);
   g.drawLine(xTip,   yTip,   xTip+4,  yTip-9); // top feather
   g.drawLine(xTip+1, yTip,   xTip+5,  yTip-9);
   g.drawLine(xTip,   yTip,   xTip+10, yTip-0); // bottom feather
   g.drawLine(xTip,   yTip+1, xTip+10, yTip+1);
   }
// ------------------
   public void draw(Graphics g)      // draw array
      {
      int j, k, x, y;

      if(drawMode==1)                   // draw only one person
         {
         g.setColor(Color.lightGray);   // clear text area
         g.fillRect(leftMargin, noteBoxTop, noteBoxWidth,
                    noteBoxHeight);
                                        // (to erase arrow)
         if(oldCurList >= topDisplayLine &&
                      oldCurList < topDisplayLine+linesInView)
            drawLink(g, oldCurList, oldCurLink);
         if(curList >= topDisplayLine &&
                      curList < topDisplayLine+linesInView)
            drawLink(g, curList, curLink);

         }
      else  // drawMode is 2 or 3       // draw all persons
         {
         if(drawMode==2)                // major redraw
            {
            g.setColor(Color.lightGray); // clear entire screen
            g.fillRect(0, 0, appletWidth, appletHeight);
            }
         else                           // drawMode=3 (for fill)
            {
            g.setColor(Color.lightGray); // clear text area
            g.fillRect(leftMargin, noteBoxTop, noteBoxWidth,
                       noteBoxHeight);
            }
         for(j=0; j<totalBuckets; j++)  // draw all buckets,
            {                           // if they're in window
            if(j>=topDisplayLine && j<topDisplayLine+linesInView)
               {
               drawLink(g, j, 0);
                                        // draw non-null links
               for(k=1; k<bucketArray[j].nLinks; k++)
                  if(bucketArray[j].linkArray[k] != null)
                     drawLink(g, j, k);
                  else                  // quit on fisetValuesrst null
                     break;
               }  // end if
            }  // end for
         }  // end if drawMode is 2 or 3

      g.setColor(Color.black);          // draw text ('note')
      g.drawString(note, leftMargin+6,
                   noteBoxTop+textHeight+6);
      drawMode = 2;
      }  // end draw()
// ------------------
   public void setDrawMode(int mode)
      { drawMode = mode; }
// ------------------
   }  // end class personGroup
////////////////////////////
public class HashChain extends java.applet.Applet
                 implements Runnable, ActionListener,
                            AdjustmentListener  // scrollbar
   {
   private Thread runner;
   private personGroup thePersonGroup;
   private int GPNumber = -1;      // general-purpose number
   private boolean isNumber = false;  // is GPNumber valid
   private TextField tf = new TextField("", 4);
   private Button newButton, fillButton, insButton,
           findButton, delButton;
   private Scrollbar sbar;
   private int scrollValue, scrollRange, linesInView;
// ------------------
   public void init()
      {
                                  // start with N cells
      thePersonGroup = new personGroup(25);
      thePersonGroup.doFill(25);  // fill in some persons

      setLayout( new BorderLayout() );   // for scroll bar
                                  // make scroll bar
      scrollRange = thePersonGroup.getScrollRange();
      linesInView = thePersonGroup.getLinesInView() - 1;
      sbar = new Scrollbar(Scrollbar.VERTICAL,
                            0, linesInView, 0, scrollRange);
      add("East",  sbar);        // add the scroll bar
      sbar.addAdjustmentListener(this);

      resize( 440, 320 );         //**for jdk1.1.4**, otherwise
                                  //    scroll bar is too long

      Panel p1 = new Panel();     // everything but scroll bar
      add("North", p1);
      p1.setLayout( new FlowLayout() );

      Panel p2 = new Panel();     // panel for buttons
      p1.add(p2);
      p2.setLayout( new FlowLayout(FlowLayout.LEFT) );

      newButton = new Button("New");     // New button
      p2.add(newButton);
      newButton.addActionListener(this);

      fillButton = new Button("Fill");   // Fill button
      p2.add(fillButton);
      fillButton.addActionListener(this);

      insButton = new Button("Ins");     // Ins button
      p2.add(insButton);
      insButton.addActionListener(this);

      findButton = new Button("Find");   // Find button
      p2.add(findButton);
      findButton.addActionListener(this);

      delButton = new Button("Del");     // Del button
      p2.add(delButton);
      delButton.addActionListener(this);

      Panel p4 = new Panel();     // panel for text field
      p1.add(p4);
      p4.setLayout( new  FlowLayout(FlowLayout.RIGHT) );
      p4.add( new Label("Enter number: ") );
      p4.add(tf);
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
         {
         thePersonGroup.newArray(isNumber, GPNumber);
                                              // reset scroll
         scrollRange = thePersonGroup.getScrollRange();
         sbar.setValues(0, linesInView, 0, scrollRange);
         }
      else if(event.getSource()==fillButton)  // "Fill" button
         {                                    // view line 0
         thePersonGroup.fill(isNumber, GPNumber);
         sbar.setValue(scrollValue);
         }
      else if(event.getSource()==insButton)   // "Ins" button
         {
         thePersonGroup.insert(isNumber, GPNumber);
         int newScrollValue = thePersonGroup.getScrollValue();
         if( newScrollValue != scrollValue )  // change scroll
            {
            scrollValue = newScrollValue;
            sbar.setValue(scrollValue);
            thePersonGroup.setDrawMode(2);
            }
         }
      else if(event.getSource()==findButton)  // "Find" button
         {
         thePersonGroup.find(isNumber, GPNumber);
         int newScrollValue = thePersonGroup.getScrollValue();
         if( newScrollValue != scrollValue )  // change scroll
            {
            scrollValue = newScrollValue;
            sbar.setValue(scrollValue);
            thePersonGroup.setDrawMode(2);
            }
         }
      else if(event.getSource()==delButton)   // "Del" button
         {
         thePersonGroup.delete(isNumber, GPNumber);
         int newScrollValue = thePersonGroup.getScrollValue();
         if( newScrollValue != scrollValue )  // change view
            {
            scrollValue = newScrollValue;
            sbar.setValue(scrollValue);
            thePersonGroup.setDrawMode(2);
            }
         }
      repaint();                        // all events
      try{ Thread.sleep(10); }
      catch(InterruptedException e)
         {  }
      }  // end actionPerformed()
// ------------------
                                     // scroll bar
   public void adjustmentValueChanged(AdjustmentEvent event)
      {
      scrollValue = sbar.getValue(); // set top line
      thePersonGroup.setScrollValue(scrollValue);
      sbar.setValue(scrollValue);    // (needed for jdk1.1.3)
      repaint();
      }  // end handleEvent()
// ------------------
   public void run()
      {
      while(true)
         {  }
      }  // end run()
// ------------------
   }  // end class HashChain
//////////////////////////


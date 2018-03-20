// LinkList.java
// demonstrates Linked List
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
class personGroup
   {
   private final int appletWidth = 440;
   private final int appletHeight = 300;
   private final int topMargin = 80;     // top of cell array
   private final int leftMargin = 10;
   private final int textHeight = 13;
   private final int hF1 = 11;           // fudge factors to
   private final int hF2 = 5;            // position numbers
   private final int hF3 = 0;            // within cells
   private final int vF = 8;
   private final int nColumns = 7;       // columns in display
   private final int nRows = 4;
   private final int columnWidth = 57;
   private final int linkWidth = 35;
   private final int interLink = columnWidth - linkWidth - 2;
   private final int linkHeight = 17;
   private final int digits3Width = 18;
   private final int rowHeight = 57;
   private final int noteBoxTop = topMargin - 25;
   private final int noteBoxHeight = 25;
   private final int noteBoxWidth = 300;
   private final int ASIZE = 28;  // maximum number of links
   private final int MAX_KEY = 999;

   private link linkArray[];      // array for holding links
   private int totalLinks;        // current number of links
   private person tempPers;       // for insert()
   private String note;           // text displayed on screen
   private int fillValue;         // value from user for fill
   private int insKey;            // key from user for insert()
   private int findKey;           // key from user for find()
   private int delKey;            // key from user for delete()
   private int codePart;          // which part of sequence?
   private int codePart2;         //    ditto for fill()
   private int opMode;            // 1=Fill, 2=Ins, etc.
   private int curIn;             // current index
   private int oldCurIn;
   private int drawMode;          // 1 = one person, 2 = all pers
   private boolean notSorted;     // not sorted versus sorted
   private boolean isOKChangeSort;
   private int insDex;            // about-to-be-inserted node
   private boolean areInserting;
   private boolean insertAtEnd;
   private int delDex;            // about-to-be-deleted node
   private boolean areDeleting;
// ------------------
   public personGroup()           // constructor
      {
      linkArray = new link[ASIZE];
      totalLinks = 0;
      curIn = oldCurIn = 0;
      codePart = 1;
      codePart2 = 1;
      drawMode = 2;
      note = "Press any button";
      notSorted = true;
      isOKChangeSort = false;
      areInserting = false;
      }  // end constructor
// ------------------
   // return a person of specified height and random RGB color
   private person makePerson(int height)
      {
      int red = 100 + (int)(java.lang.Math.random()*154);
      int green = 100 + (int)(java.lang.Math.random()*154);
      int blue = 100 + (int)(java.lang.Math.random()*154);
      Color newColor = new Color(red, green, blue);
      return new person(height, newColor);
      }
// ------------------
   public boolean getSortStatus()
      { return notSorted; }
// ------------------
   public boolean getChangeStatus()
      { return isOKChangeSort; }
// ------------------
   public void setSortStatus(boolean nosortButton)
      {
      if(isOKChangeSort && nosortButton != notSorted)
         notSorted = nosortButton;
      if(!isOKChangeSort)
         note = "To change sort status, create list with New";
      drawMode = 1;
      }
// ------------------
   // create and fill a new linked list of specified size
   public void newList(boolean isNumb, int userVal)
      {
      areInserting = false;
      areDeleting = false;
      if(opMode != 1)
         {
         opMode = 1;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            note = "Enter size of linked list to create";
            drawMode = 1;
            codePart = 2;
            oldCurIn = curIn;
            curIn = 0;
            break;
         case 2:
            if(!isNumb || userVal < 0 || userVal > ASIZE)
               {
               note = "ERROR: use size between 0 and " + ASIZE;
               codePart = 1;      // inappropriate size
               }
            else
               {
               note = "Will create list with "
                                       + userVal + " links";
               codePart = 3;
               }
            drawMode = 1;
            break;
         case 3:
            note = "Select unsorted or sorted data";
            isOKChangeSort = true;
            drawMode = 1;
            codePart = 4;
            break;
         case 4:
            if(notSorted)
               note = "Data will not be sorted";
            else
               note = "Data will be sorted";
            isOKChangeSort = false;
            totalLinks = 0;
            drawMode = 2;
            codePart = 5;
            break;
         case 5:
            totalLinks = userVal;
            doFill(totalLinks);
            note = "New list created; total links = " +
                                                   totalLinks;
            oldCurIn = curIn;
            curIn = 0;
            drawMode = 2;
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
   public void doFill(int tlinks)
      {
      totalLinks = tlinks;
      int j, randVal;
      for(j=0; j<ASIZE; j++) // clear entire array
         linkArray[j] = null;
      oldCurIn = curIn;
      curIn = 0;
      codePart = 1;
      if(notSorted)                  // insert random data
         {
         for(j=0; j<totalLinks; j++) // fill with links
            {
            randVal = (int)(java.lang.Math.random()*MAX_KEY);
            tempPers = makePerson(randVal);
            linkArray[j] = new link(tempPers);
            }
         }  // end if(isUnsorted)
      else                           // insert sorted data
         {
         int currentKey = 0;
         int maxRandom;
         int lastKey = 0;
         for(j=0; j<totalLinks; j++) // fill with links
            {
            maxRandom = (int)( ((float)MAX_KEY-(float)lastKey) /
                               ((float)totalLinks-(float)j) );
            randVal = (int)(java.lang.Math.random()*maxRandom);
            currentKey += randVal;
            lastKey = currentKey;
            tempPers = makePerson(currentKey);
            linkArray[j] = new link(tempPers);
            }
         }
      }  // end doFill
// ------------------
   // insert a person
   public void insert(boolean isNumb, int userVal)
      {
      areDeleting = false;
      if(opMode != 3)
         {
         opMode = 3;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            oldCurIn = curIn;
            curIn = 0;
            insertAtEnd = false;
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
            else if(totalLinks >= ASIZE)
               {
               note = "CAN'T INSERT: no room in display";
               codePart = 6;
               }
            else
               {
               insKey = userVal;
                                  // make person to insert
               tempPers = makePerson(insKey);
               if(notSorted)
                  {
                  note = "Will insert item with key " + insKey;
                  codePart = 4;
                  }
               else
                  {
                  note = "Will search for insertion point";
                  codePart = 3;
                  }
               }
            drawMode = 1;
            break;
         case 3:                   // search for insertion point
            if(curIn == totalLinks-1 &&    // if at end of list
               insKey > linkArray[curIn].persData.getHeight() )
               {                           // and insKey bigger,
               note = "Found insertion point at end of list";
               insertAtEnd = true;
               codePart = 5;               // forget temp link
               }
            else if( insKey >
                     linkArray[curIn].persData.getHeight() )
               {
               note = "Searching for insertion point";
               oldCurIn = curIn++;
               codePart = 3;
               }
            else
               {
               note = "Have found insertion point";
               codePart = 4;
               }
            drawMode = 1;
            break;
         case 4:                   // draw temporary new link
            areInserting = true;
            if(notSorted)
               insDex = 0;
            else
               insDex = curIn;
            note = "Inserted item; will redraw list";
            drawMode = 1;
            codePart = 5;
            break;
         case 5:                  // redraw entire list
            if(insertAtEnd)             // if at end of list
               {
               oldCurIn = curIn++;
               note = "Inserted item with key " + insKey +
                      " at end of list";
               }
            else                        // not at end
               {
               areInserting = false;    // move links
               for(int j=totalLinks; j>curIn; j--)
                  linkArray[j] = linkArray[j-1];
               note="Inserted item with key " + insKey;
               }
            linkArray[curIn] = new link(tempPers);
            totalLinks++;
            drawMode = 2;
            codePart = 6;
            break;
         case 6:
            note = "Insertion completed; total items = "
                                               + totalLinks;
            drawMode = 1;
            codePart = 7;
            break;
         case 7:
            oldCurIn = curIn;
            curIn = 0;
            note = "Press any button";
            drawMode = 1;
            codePart = 1;
            break;
         }  // end switch
      }  // end insert()
// ------------------
   public void find(boolean isNumb, int userVal)
      {
      areInserting = false;
      areDeleting = false;
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
               note="ERROR: use key between 0 and " + MAX_KEY;
               codePart = 1;      // inappropriate person number
               }
            else
               {
               findKey = userVal;
               oldCurIn = curIn;
               curIn = 0;
               note = "Looking for item with key " + findKey;
               codePart = 3;
               }
            break;
         case 3:
            if(linkArray[curIn].persData.getHeight() == findKey)
               {                            // match
               note="Have found item with key " + findKey;
               codePart = 6;
               }
            else if(curIn == totalLinks-1 || // last cell or
             ( !notSorted &&        // sorted and too big
               linkArray[curIn].persData.getHeight() > findKey) )
               {
               note="Can't locate item with key " + findKey;
               codePart = 6;
               }
            else
               {
               note = "Searching for item with key " + findKey;
               oldCurIn = curIn++;
               codePart = 3;
               }
            break;
         // no cases 4 or 5
         case 6:
            oldCurIn = curIn;
            curIn = 0;
            note = "Press any button";
            codePart = 1;
            break;
         }  // end switch
      drawMode = 1;             // no changes during find
      }  // end find()
// ------------------
   public void delete(boolean isNumb, int userVal)
      {
      areInserting = false;
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
               note="ERROR: use key between 0 and " + MAX_KEY;
               codePart = 1;      // inappropriate person number
               }
            else
               {
               delKey = userVal;
               oldCurIn = curIn;
               curIn = 0;
               note = "Looking for item with key " + delKey;
               codePart = 3;
               }
            drawMode = 1;
            break;
         case 3:
            if(linkArray[curIn].persData.getHeight() == delKey)
               {                            // match
               note = "Have found item with key " + delKey;
               if(curIn == totalLinks-1)  // if last item on list
                  codePart = 5;
               else                       // not last item
                  codePart = 4;
               }
            else if(curIn == totalLinks-1 || // last cell or
             ( !notSorted &&        // sorted and too big
              linkArray[curIn].persData.getHeight() > delKey) )
               {
               note="Can't locate item with key " + delKey;
               codePart = 6;
               }
            else
               {
               note = "Searching for item with key " + delKey;
               oldCurIn = curIn++;
               codePart = 3;
               }
            drawMode = 1;
            break;
         case 4:                  // draw temporary new link
            areDeleting = true;
            delDex = curIn;
            note = "Deleted item; will redraw list";
            drawMode = 1;
            codePart = 5;
            break;
         case 5:                  // redraw entire list
            areDeleting = false;
            for(int j=curIn; j<totalLinks-1; j++)
               linkArray[j] = linkArray[j+1];
            totalLinks--;
            oldCurIn = curIn;
            curIn = 0;
            note="Deleted item with key " + delKey;
            drawMode = 2;
            codePart = 6;
            break;
         case 6:
            oldCurIn = curIn;
            curIn = 0;
            note = "Press any button";
            codePart = 1;
            break;
         }  // end switch
      }  // end delete()
// ------------------
   public void drawLink(Graphics g, int persDex)
      {
      int x, y;
      int hF, height;
      x = leftMargin + 22 + columnWidth * (persDex % nColumns);
      y = topMargin + 9 + rowHeight * (persDex / nColumns);
      if(linkArray[curIn] != null)   // don't draw null links
         {
         g.setColor(Color.black);
         g.drawRect(x, y-5, linkWidth, linkHeight);
                                     // get height and color
         height = linkArray[persDex].persData.getHeight();
         g.setColor( linkArray[persDex].persData.getColor() );
                                     // fill rectangle with color
         g.fill3DRect(x+1, y-4, linkWidth-1,
                                             linkHeight-1, true);
         if(height<10)       hF = hF1;  // fudge factors
         else if(height<100) hF = hF2;  // for digits
         else                hF = hF3;
         g.setColor(Color.black);    // draw height number
         g.drawString(""+height, x+hF+10, y+linkHeight-vF);
                                     // draw linkage arrow
         if(persDex < totalLinks-1)  // if not last link
            {                        // if not at end of row
            if(persDex % nColumns != nColumns-1)
              {
              g.drawLine(x+linkWidth,          y+linkHeight/2-4,
                         x+linkWidth+interLink, y+linkHeight/2-4);
              smallArrow(g, x+linkWidth+interLink, y+linkHeight/2-4);
              }                      // at end of row,
                                     // and haven't deleted last,
            else // if( !(areDeleting && delDex==totalLinks-1) )
               {                        // draw line to next row
               int yEnd = y+linkHeight/2 - 4;
               g.drawLine(x+linkWidth,   yEnd,          // right
                          x+linkWidth+8, yEnd);
               g.drawLine(x+linkWidth+8, yEnd,          // down
                          x+linkWidth+8, yEnd + 2*linkHeight + 4);
                                                        // left
               g.drawLine(x+linkWidth+8, yEnd + 2*linkHeight + 4,
                          leftMargin+0,  yEnd + 2*linkHeight + 4);
                                                        // down
               g.drawLine(leftMargin+0, yEnd + 2*linkHeight + 4,
                          leftMargin+0, yEnd + rowHeight);
                                                        // right
               g.drawLine(leftMargin,          yEnd+rowHeight,
                          leftMargin+interLink, yEnd+rowHeight);
                smallArrow(g, leftMargin+interLink, yEnd+rowHeight);
               }  // end else(end of row)
            }  // end if(not last link)
         }  // end if(link not null)
                                     // draw big red arrow
      if( persDex==curIn && !areInserting)
        g.setColor(Color.red);       //   (curIn = red arrow
     else                            //    other persons =
        g.setColor(Color.lightGray); //    gray arrow)
     int xTip = x + linkWidth/2;
     int yTip = y + linkHeight - 3;
     g.drawLine(xTip,   yTip, xTip,    yTip+19); // shaft
     g.drawLine(xTip+1, yTip, xTip+1,  yTip+19);
     g.drawLine(xTip,   yTip, xTip+6,  yTip+10); // right feather
     g.drawLine(xTip+1, yTip, xTip+7,  yTip+10);
     g.drawLine(xTip,   yTip, xTip-6,  yTip+10); // left feather
     g.drawLine(xTip+1, yTip, xTip-5,  yTip+10);
     }
// ------------------
   private void drawInsertLink(Graphics g)
      {
      int x, y;
      int hF, height;
      x = leftMargin + 5 + columnWidth * (insDex % nColumns);
      y = topMargin + 35 + rowHeight * (insDex / nColumns);
      g.setColor(Color.black);
      g.drawRect(x, y-5, linkWidth, linkHeight);

      height = tempPers.getHeight(); // get height and color
      g.setColor( tempPers.getColor() );
                                     // fill rectangle with color
      g.fill3DRect(x+1, y-4, linkWidth-1, linkHeight-1, true);
      if(height<10)       hF = hF1;  // fudge factors for digits
      else if(height<100) hF = hF2;
      else                hF = hF3;
      g.setColor(Color.black);       // draw height number
      g.drawString(""+height, x + hF + 10, y + linkHeight - vF);
      int yEnd = y+linkHeight/2 - 3;

      if(insDex != 0)                // line: last node to this
         {
         g.setColor(Color.lightGray);            // erase
         g.drawLine(x-4,  yEnd-27,               // old
                    x+8+7, yEnd-27);             // line
         g.setColor(Color.black);
         g.drawLine(x-4, yEnd-27, x+2, yEnd-27); // right
         g.drawLine(x+2, yEnd-27, x+2, yEnd-14); // down
         g.drawLine(x+2, yEnd-14, x-8, yEnd-14); // left
         g.drawLine(x-8, yEnd-14, x-8, yEnd-1);  // down
         g.drawLine(x-8, yEnd-1,  x-1, yEnd-1);  // right
         smallArrow(g, x-1, yEnd-1);             // feathers
         }
                                    // line: this node to next
      g.drawLine(x+linkWidth,   yEnd-1,          // right
                 x+linkWidth+8, yEnd-1);
      g.drawLine(x+linkWidth+8, yEnd-1,          // up
                 x+linkWidth+8, yEnd-14);
      g.drawLine(x+linkWidth+8, yEnd-14,         // left
                 x+8, yEnd-14);
      g.drawLine(x+8, yEnd-14,                   // up
                 x+8, yEnd-27);
      g.drawLine(x+8, yEnd-27,                   // right
                 x+8+7, yEnd-27);
      smallArrow(g, x+8+7, yEnd-27);             // feathers
      }  // end drawInsertLink()
// ------------------
   private void drawDeleteLink(Graphics g)
      {
      int x, y;
      x = leftMargin + 22 + columnWidth * (delDex % nColumns);
      y = topMargin + 9 + rowHeight * (delDex / nColumns);
      g.setColor(Color.lightGray);    // blank box erases link
      g.fillRect(x-10, y-5, linkWidth+11, linkHeight+1);
      if(delDex==totalLinks-1)        // if last link,
         g.setColor(Color.lightGray); // erase arrow-to-next
      else                            // otherwise, draw
         g.setColor(Color.black);     // line over blank box
      g.drawLine(x-interLink-1, y+linkHeight/2-4,
                 x+linkWidth+7, y+linkHeight/2-4);


      }  // end drawDeleteLink()
// ------------------
   private void smallArrow(Graphics g, int xTip, int yTip)
      {
      g.drawLine(xTip, yTip, xTip-5,  yTip-3);  // upper feather
      g.drawLine(xTip, yTip, xTip-5,  yTip+3);  // lower feather
      }
// ------------------
   public void draw(Graphics g)         // draw array
      {
      int j, x, y;

      if(drawMode==1)                   // draw only one link
         {
         g.setColor(Color.lightGray);   // clear text area
         g.fillRect(leftMargin, noteBoxTop, noteBoxWidth,
                    noteBoxHeight);
         g.setColor(Color.black);       // draw 'note'
         g.drawString(note, leftMargin+6,
                      noteBoxTop+textHeight+6);

         drawLink(g, oldCurIn);         // (to erase arrow)
         drawLink(g, curIn);            // draw current person
         drawMode = 2;
         }
      else                              // draw all links
         {
         g.setColor(Color.lightGray);   // clear entire screen
         g.fillRect(0, 0, appletWidth, appletHeight);

         for(j=0; j<totalLinks; j++)
            drawLink(g, j);
         g.setColor(Color.black);       // draw text ('note')
         g.drawString(note, leftMargin+6,
                      noteBoxTop+textHeight+6);
         }  // end else(drawMode is 2)
      if(areInserting)                  // draw new node
         drawInsertLink(g);             // between rows
      else if(areDeleting)
         drawDeleteLink(g);
      }  // end draw()
// ------------------
   }  // end class personGroup
////////////////////////////
public class LinkList extends java.applet.Applet
                     implements Runnable, ActionListener,
                     ItemListener
   {
   private Thread runner;
   private personGroup thePersonGroup;
   private int GPNumber = -1;      // general-purpose number
   private boolean isNumber = false;  // is GPNumber valid
   private TextField tf = new TextField("", 4);
   private Checkbox nosort, sort;
   private Button newButton, insButton, findButton, delButton;
// ------------------
   public void init()
      {
      setLayout( new FlowLayout() );
      Panel p1 = new Panel();
      add(p1);
      p1.setLayout( new FlowLayout() );

      Panel p2 = new Panel();     // buttons
      p1.add(p2);
      p2.setLayout( new FlowLayout(FlowLayout.LEFT) );

      newButton = new Button("New");      // New button
      p2.add(newButton);
      newButton.addActionListener(this);

      insButton = new Button("Ins");      // Ins button
      p2.add(insButton);
      insButton.addActionListener(this);

      findButton = new Button("Find");    // Find button
      p2.add(findButton);
      findButton.addActionListener(this);

      delButton = new Button("Del");      // Del button
      p2.add(delButton);
      delButton.addActionListener(this);

      Panel p3 = new Panel();     // checkboxes for sort/nosort
      p1.add(p3);
      p3.setLayout( new GridLayout(2, 1) );
      CheckboxGroup theGroup = new CheckboxGroup();

      nosort = new Checkbox("Unsorted", true, theGroup);
      p3.add(nosort);
      nosort.addItemListener(this);

      sort = new Checkbox("Sorted", false, theGroup);
      p3.add(sort);
      sort.addItemListener(this);

      Panel p4 = new Panel();     // text field
      p1.add(p4);
      p4.setLayout( new  FlowLayout(FlowLayout.RIGHT) );
      p4.add( new Label("Enter number: ") );
      p4.add(tf);
      thePersonGroup = new personGroup();
      thePersonGroup.doFill(13);  // make 13 initial links
      repaint();
      }
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
      if(event.getSource()==newButton)         // "New" button
         thePersonGroup.newList(isNumber, GPNumber);
      else if(event.getSource()==insButton)    // "Ins" button
         thePersonGroup.insert(isNumber, GPNumber);
      else if(event.getSource()==findButton)   // "Find" button
         thePersonGroup.find(isNumber, GPNumber);
      else if(event.getSource()==delButton)    // "Del" button
         thePersonGroup.delete(isNumber, GPNumber);

      repaint();                        // all events
      try{ Thread.sleep(10); }
      catch(InterruptedException e)
         {  }
      }  // end actioPerformed()
// ------------------
   public void itemStateChanged(ItemEvent event)
      {
      boolean isUnsorted = event.getSource() == nosort;
      boolean wasUnsorted = thePersonGroup.getSortStatus();
      boolean canChange = thePersonGroup.getChangeStatus();
      thePersonGroup.setSortStatus(isUnsorted);

      if( (isUnsorted && canChange && !wasUnsorted) ||
          (!isUnsorted && !canChange && wasUnsorted) )
         {
         nosort.setState(true);
         sort.setState(false);
         }
      if( (!isUnsorted && canChange && wasUnsorted) ||
          (isUnsorted && !canChange && !wasUnsorted) )
         {
         nosort.setState(false);
         sort.setState(true);
         }
      }  // end itemStateChanged()
// ------------------
   public void run()
      {
      while(true)
         {
         }
      }  // end run()
// ------------------
   }  // end class LinkedList
//////////////////////////


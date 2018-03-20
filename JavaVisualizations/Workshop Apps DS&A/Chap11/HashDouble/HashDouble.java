// HashDouble.java
// demonstrates hash tables,
// with quadratic probe or double hashing
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
class personGroup
   {
   private final int appletWidth = 440;
   private final int appletHeight = 300;
   private final int topMargin = 80;     // top of cell array
   private final int leftMargin = 10;
   private final int textHeight = 13;
   private final int hF1 = 12;           // fudge factors to
   private final int hF2 = 6;            // position numbers
   private final int hF3 = 0;            // within cells
   private final int vF = 8;
   private final int nCellsPerCol = 12;  // cells per column
   private final int columnWidth = 85;
   private final int cellWidth = 35;
   private final int cellHeight = 17;
   private final int digits3Width = 18;
   private final int vertSeparation = cellHeight + 2;
   private final int horizSeparation = cellWidth + 25;
   private final int noteBoxTop = topMargin - 25;
   private final int noteBoxHeight = 25;
   private final int noteBoxWidth = 300;
   private final int ASIZE = 60;  // maximum size of array
   private final int MAX_KEY = 999;

   private person personArray[];  // array for holding persons
   private int totalCells;        // current array size
   private int nPersons;          // persons inserted so far
   private person tempPers;       // for insert()
   private String note;           // text displayed on screen
   private int fillValue;         // value from user for fill
   private int insKey;            // key from user for insert
   private int findKey;           // key from user for find
   private int codePart;          // which part of sequence?
   private int opMode;            // 1=Fill, 2=Ins, etc.
   private int curIn;             // current index
   private int oldCurIn;
   private int drawMode;          // 1 = one person, 2 = all pers
   private boolean isProbeDouble; // double or quad
   private boolean isOKChangeProbe;
   private boolean isCollision;
   private int stepSize;
   private int stepSizeCount;     // for quad probe
   private int origCurIn;         // for quad probe
// ------------------
   public personGroup(int cells)           // constructor
      {
      totalCells = cells;
      personArray = new person[totalCells];
      curIn = oldCurIn = 0;
      nPersons = 0;
      codePart = 1;
      stepSize = 1;
      isProbeDouble = true;
      isOKChangeProbe = false;
      isCollision = false;
      drawMode = 2;
      note = "Press any button";
      }  // end constructor
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
   public boolean probeDouble()
      { return isProbeDouble; }
// ------------------
   public boolean changeProbeOK()
      { return isOKChangeProbe; }
// ------------------
   public void setProbe(boolean doubleButton)
      {
      if(isOKChangeProbe && doubleButton != isProbeDouble)
         isProbeDouble = doubleButton;
      if(!isOKChangeProbe)
         note = "To change probe, create array with New";
      drawMode = 1;
      }
// ------------------
   // create a new empty array of specified size
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
            note = "Enter size of array to create";
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
               totalCells = userVal;
               note = "Will create empty array with "
                                       + totalCells + " cells";
               codePart = 3;
               }
            drawMode = 1;
            break;
         case 3:
            note = "Select Double or Quadratic probe";
            isOKChangeProbe = true;
            drawMode = 1;
            codePart = 4;
            break;
         case 4:
            personArray = new person[totalCells];
            for(int j=0; j<totalCells; j++)  // put null in
               personArray[j] = null;        // all cells
            nPersons = 0;

            if(isProbeDouble)
               note = "Will use double hashing";
            else
               note = "Will use quadratic probe";
            isOKChangeProbe = false;
            drawMode = 2;
            codePart = 5;
            break;
         case 5:
            note = "New array created; total items = " +
                                                   nPersons;
            oldCurIn = curIn;
            curIn = 0;
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
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            note = "Enter number of items to fill in";
            drawMode = 1;
            codePart = 2;
            break;
         case 2:
            if(isNumb != true || userVal<0 || userVal>totalCells)
               {
               note = "ERROR: can't fill more than "
                                   + totalCells + " items";
               drawMode = 1;
               codePart = 1;
               codePart = 1;
               }
            else
               {
               fillValue = userVal;
               note = "Will fill in " + fillValue + " items";
               drawMode = 1;
               codePart = 3;
               }
            break;
         case 3:
            nPersons = 0;
            doFill(fillValue);
            oldCurIn = curIn;
            curIn = 0;
            drawMode = 3;
            codePart = 4;
            break;
         case 4:
            note = "Press any button";
            drawMode = 1;
            codePart = 1;
            break;
         }  // end switch
      }  // end fill
// ------------------
   public void doFill(int totalPersons)
      {
      int j, randVal;
      for(j=0; j<totalCells; j++) // clear the array
         personArray[j] = null;
      oldCurIn = curIn;
      codePart = 1;
      while(nPersons < totalPersons)
         {                               // generate random key
         randVal = (int)(java.lang.Math.random()*MAX_KEY);
         while( getDuplicate(randVal) != -1 )
            randVal = (int)(java.lang.Math.random()*MAX_KEY);

         tempPers = makePerson(randVal);  // make new item
         curIn = hashFunction(randVal);   // get hash value
         if(isProbeDouble)     // double hashing
            stepSize = hashFunction2(randVal);
         else                  // quadratic probing
            {
            origCurIn = curIn;
            stepSizeCount = 1;
            stepSize = 1;
            }

         while(personArray[curIn] != null)
            {
            if(stepSize > 100000)
               {
               note = "Can't complete fill; total items = " +
                                                     nPersons;
               return;
               }
            oldCurIn = curIn;
            if(isProbeDouble)
               curIn = (curIn+stepSize) % totalCells;
            else                         // quadratic probe
               {
               curIn = (origCurIn + stepSize) % totalCells;
               stepSizeCount++;
               stepSize = stepSizeCount*stepSizeCount;
               }
            }  // end while
         personArray[curIn] = tempPers;  // insert new item
         nPersons++;
         }  // end while(more persons)
      note = "Fill completed; total items = " + nPersons;
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
            isCollision = false;
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
            else if(nPersons >= totalCells)
               {
               note = "CAN'T INSERT: array is full";
               codePart = 6;
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
            if( !isCollision )
               {                         // not collision mode
               oldCurIn = curIn;
               curIn = hashFunction(insKey); // get hash value
               if(personArray[curIn] == null)
                  {                      // cell not occupied
                  personArray[curIn] = tempPers;
                  nPersons++;
                  note="Inserted item with key " + insKey +
                       " at index " + curIn;
                  drawMode = 1;
                  codePart = 5;
                  break;
                  }  // end if(cell not occupied)
               else                      // cell occupied
                  {
                  note = "Cell " + curIn +
                         " occupied; going to next cell";
                  isCollision = true;
                  if(isProbeDouble)     // double hashing
                     stepSize = hashFunction2(insKey);
                  else                  // quadratic probing
                     {
                     origCurIn = curIn;
                     stepSize = 1;
                     stepSizeCount = 1;
                     }
                  drawMode = 1;
                  codePart = 3;
                  break;
                  }  // end else cell occupied
               }  // end if(not old collision)
            // seeking empty cell following collision
            else                         // collision mode
               {
               if(personArray[curIn] == null)
                  {                      // empty cell
                  personArray[curIn] = tempPers;
                  nPersons++;            // insert person
                  note="Inserted item with key " + insKey +
                       " at index "+curIn;
                  isCollision = false;
                  drawMode = 1;
                  codePart = 5;
                  break;
                  }
               else                      // this cell occupied
                  {
                  oldCurIn = curIn;
                  note =
                  "Searching for unoccupied cell; step was "
                                                  +stepSize;
                  if(isProbeDouble)
                     curIn = (curIn+stepSize) % totalCells;
                  else                   // quadratic probing
                     {
                     curIn = (origCurIn+stepSize) % totalCells;
                     stepSizeCount++;
                     stepSize = stepSizeCount*stepSizeCount;
                     }
                  codePart = 3;
                  drawMode = 1;
                  break;
                  }  // end else this cell occupied
               }  // end else old collision
         // no case 4
         case 5:
            note = "Insertion completed; total items = "
                                               + nPersons;
            drawMode = 1;
            codePart = 6;
            break;
         case 6:
            oldCurIn = curIn;
            curIn = 0;
            note = "Press any button";
            drawMode = 1;
            codePart = 1;
            break;
         }  // end switch
      }  // end insert()
// ------------------
   public int getDuplicate(int value)
      {
      for(int j=0; j<totalCells; j++)
         if(personArray[j] != null &&
            personArray[j].getHeight() == value)
            return j;                       // duplicate
      return -1;                            // no duplicate
      }
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
               note="ERROR: use key between 0 and " + MAX_KEY;
               codePart = 1;      // inappropriate person number
               }
            else
               {
               findKey = userVal;
               oldCurIn = curIn;
               curIn = hashFunction(findKey); // get hash value
               isCollision = false;
               note = "Looking for item with key " + findKey +
                      " at index " + curIn;
               codePart = 3;
               }
            break;
         case 3:
            if(personArray[curIn] == null)
               {                            // cell not occupied
               note="Can't locate item with key " + findKey;
               codePart = 6;
               }
            else if(personArray[curIn].getHeight() == findKey)
               {                            // match
               note="Have found item with key " + findKey;
               codePart = 6;
               }
            // cell occupied, but no match
            else if( !isCollision )         // not old collision
               {
               note = "No match; will start probe";
               isCollision = true;
               if(isProbeDouble)            // double hashing
                  stepSize = hashFunction2(findKey);
               else                         // quadratic probing
                  {
                  origCurIn = curIn;
                  stepSize = 1;
                  stepSizeCount = 1;
                  }
               codePart = 3;
               }  // end if(not old collision)
            else                            // isCollision
               {
               oldCurIn = curIn;
               note = "Checking next cell; step was " +
                                                  stepSize;
               if(isProbeDouble)
                  curIn = (curIn+stepSize) % totalCells;
               else                        // quadratic probe
                  {
                  curIn = (origCurIn+stepSize) % totalCells;
                  stepSizeCount++;
                  stepSize = stepSizeCount*stepSizeCount;
                  }
               codePart = 3;
               }  // end else old collision
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
   private int quickFind(int key)
      {
      int index = hashFunction(key);
      if(personArray[index] == null)
         return -1;                        // not there
      else if(personArray[index].getHeight() == key)
         return index;                     // found it
      else  // cell occupied, but no match; start probe
         {
         if(isProbeDouble)
            stepSize = hashFunction2(key);
         else
            {
            stepSize = 1;
            stepSizeCount = 1;
            }
         for(int j=0; j<totalCells; j++)
            {
            index = (index+stepSize) % totalCells;
            // (no step-size change needed if double hash)
            if(!isProbeDouble)            // quadratic probe
               {
               stepSizeCount++;
               stepSize = stepSizeCount*stepSizeCount;
               }
            if(personArray[index] == null)
               return -1;
            else if(personArray[index].getHeight() == key)
               return index;
            }  // end for
         }  // end else
      return -1;          // have looked at all cells (?)
                          // can't find it
      }  // end quickFind()
// ------------------
   // returns index resulting from hashing person's height
   public int hashFunction(int key)
      {
   //   return (key*10 + key + key/10 + key/100) % totalCells;
      return key % totalCells;
      }
// ------------------
   // returns step size derived from key, for double hashing
   public int hashFunction2(int key)
      {
      return 7 - key % 7;
      }
// ------------------
 public void drawPerson(Graphics g, int persDex)
   {
   int x, y;
   int hF, height;

   x = leftMargin + columnWidth * (persDex / nCellsPerCol);
   y = topMargin + 9 + cellHeight * (persDex % nCellsPerCol);

   if(persDex<10)       hF = hF1;  // fudge factors for digits
   else if(persDex<100) hF = hF2;
   else                 hF = hF3;

   if(drawMode==2)
      {
      g.setColor(Color.black);     // draw array index
      g.drawString(""+persDex, x + hF, y + cellHeight - vF);
      }
   g.setColor(Color.black);        // draw rectangle
   g.drawRect(x+digits3Width+5, y-5, cellWidth, cellHeight);

   if(personArray[persDex]==null)  // if cell not occupied,
      {
      g.setColor(Color.lightGray); // fill rectangle w/ backgnd
      g.fill3DRect(x+digits3Width+6, y-4, cellWidth-1,
                                          cellHeight-1, true);
      }
   else                            // cell is occupied
      {                            // get height and color
      height = personArray[persDex].getHeight();
      g.setColor( personArray[persDex].getColor() );
                                   // fill rectangle with color
      g.fill3DRect(x+digits3Width+6, y-4, cellWidth-1,
                                          cellHeight-1, true);
      if(height<10)       hF = hF1; // fudge factors for digits
      else if(height<100) hF = hF2;
      else                hF = hF3;
      g.setColor(Color.black);     // draw height number
      g.drawString(""+height, x + digits3Width + hF +15,
                              y + cellHeight - vF);
      }

   if( persDex==curIn )            // draw arrow
      g.setColor(Color.red);         // for curIn, red arrow
   else                              // for all other persons,
      g.setColor(Color.lightGray);   // gray arrow
   int xTip = x + digits3Width + 8 + cellWidth;
   int yTip = y + cellHeight / 2 - 4;
   g.drawLine(xTip, yTip,   xTip+20, yTip);    // shaft
   g.drawLine(xTip, yTip+1, xTip+20, yTip+1);
   g.drawLine(xTip, yTip,   xTip+5,  yTip-5);  // top feather
   g.drawLine(xTip, yTip+1, xTip+5,  yTip-4);
   g.drawLine(xTip, yTip,   xTip+5,  yTip+5);  // bottom feather
   g.drawLine(xTip, yTip+1, xTip+5,  yTip+6);
   }
// ------------------
   public void draw(Graphics g)      // draw array
      {
      int j, x, y;

      if(drawMode==1)                   // draw only one person
         {
         g.setColor(Color.lightGray);   // clear text area
         g.fillRect(leftMargin, noteBoxTop, noteBoxWidth,
                    noteBoxHeight);
         g.setColor(Color.black);       // draw 'note'
         g.drawString(note, leftMargin+6,
                      noteBoxTop+textHeight+6);

         drawPerson(g, oldCurIn);       // (to erase arrow)
         drawPerson(g, curIn);          // draw current person
         drawMode = 2;
         }
      else if(drawMode==2)              // draw all persons
         {
         g.setColor(Color.lightGray);   // clear entire screen
         g.fillRect(0, 0, appletWidth, appletHeight);

         for(j=0; j<totalCells; j++)
            drawPerson(g, j);
         g.setColor(Color.black);       // draw text ('note')
         g.drawString(note, leftMargin+6,
                      noteBoxTop+textHeight+6);
         }  // end if drawMode is 2
      else                              // drawMode is 3
         {
         g.setColor(Color.lightGray);   // clear text area
         g.fillRect(leftMargin, noteBoxTop, noteBoxWidth,
                    noteBoxHeight);
         for(j=0; j<totalCells; j++)    // draw all cells
            drawPerson(g, j);
         g.setColor(Color.black);       // draw text ('note')
         g.drawString(note, leftMargin+6,
                      noteBoxTop+textHeight+6);
         }
      }  // end draw()
// ------------------
   }  // end class personGroup
////////////////////////////
public class HashDouble extends java.applet.Applet
                     implements Runnable, ActionListener,
                                ItemListener
   {
   private Thread runner;
   private personGroup thePersonGroup;
   private int GPNumber = -1;      // general-purpose number
   private boolean isNumber = false;  // is GPNumber valid
   private TextField tf = new TextField("", 4);
   private Checkbox doubleH, quad;
   private Button newButton, fillButton, insButton, findButton;
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

      fillButton = new Button("Fill");    // Fill button
      p2.add(fillButton);
      fillButton.addActionListener(this);

      insButton = new Button("Ins");      // Ins button
      p2.add(insButton);
      insButton.addActionListener(this);

      findButton = new Button("Find");    // Find button
      p2.add(findButton);
      findButton.addActionListener(this);

      Panel p3 = new Panel();     // checkboxes for probe
      p1.add(p3);
      p3.setLayout( new GridLayout(2, 1) );
      CheckboxGroup theGroup = new CheckboxGroup();

      doubleH = new Checkbox("Double", true, theGroup);
      p3.add(doubleH);
      doubleH.addItemListener(this);

      quad = new Checkbox("Quad", false, theGroup);
      p3.add(quad);
      quad.addItemListener(this);

      Panel p4 = new Panel();     // text field
      p1.add(p4);
      p4.setLayout( new  FlowLayout(FlowLayout.RIGHT) );
      p4.add( new Label("Enter number: ") );
      p4.add(tf);
                                  // start with 59 cells
      thePersonGroup = new personGroup(59);
      thePersonGroup.doFill(30);  // of which 30 are filled
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
      if(event.getSource() == newButton)        // "New" button
         thePersonGroup.newArray(isNumber, GPNumber);
      else if(event.getSource() == fillButton)  // "Fill" button
         thePersonGroup.fill(isNumber, GPNumber);
      else if(event.getSource() == insButton)   // "Ins" button
         thePersonGroup.insert(isNumber, GPNumber);
      else if(event.getSource() == findButton)  // "Find" button
         thePersonGroup.find(isNumber, GPNumber);

      repaint();                        // all events
      try{ Thread.sleep(10); }
      catch(InterruptedException e)
         {  }
      }  // end actionPerformed()
// ------------------
   public void itemStateChanged(ItemEvent event)
      {
      boolean isDouble = (event.getSource() == doubleH);
      boolean wasDouble = thePersonGroup.probeDouble();
      boolean canChange = thePersonGroup.changeProbeOK();
      thePersonGroup.setProbe(isDouble);

      if( (isDouble && canChange && !wasDouble) ||
          (!isDouble && !canChange && wasDouble) )
         {
         doubleH.setState(true);
         quad.setState(false);
         }
      if( (!isDouble && canChange && wasDouble) ||
          (isDouble && !canChange && !wasDouble) )
         {
         doubleH.setState(false);
         quad.setState(true);
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
   }  // end class HashDouble
//////////////////////////


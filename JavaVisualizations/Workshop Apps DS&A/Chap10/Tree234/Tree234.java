// Tree234.java
// demonstrates 234 tree
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
class node
   {
   private final int ORDER = 4;
   private int numPers;
   private node parent;
   private node children[] = new node[ORDER];
   private person personArray[] = new person[ORDER-1];
   private boolean weAreCurrentNode;
// ------------------
   public node()                 // constructor
      {
      parent = null;
      for(int j=0; j<ORDER-1; j++)
         personArray[j]=null;
      for(int j=0; j<ORDER; j++)
         children[j] = null;
      numPers = 0;
      weAreCurrentNode = false;
      }
// ------------------
   // connect child to this node
   public void connectChild(int childNum, node child)
      {
      children[childNum] = child;
      if(child != null)
         child.parent = this;
      }
// ------------------
   public node getChild(int childNum)
      { return children[childNum]; }
// ------------------
   // which child number of our parent?
   public int getChildNumber()
      {
      for(int j=0; j<parent.getNumPers()+1; j++)
         if(parent.getChild(j)==this)
            return j;
      return -1;         // error
      }  // end getChildNumber()
// ------------------
   public node getParent()
      { return parent; }
// ------------------
   public boolean isLeaf()
      { return (children[0]==null) ? true : false; }
// ------------------
   public int getNumPers()
     { return numPers; }
// ------------------
   public void putp(person p, int i) // put person at index
      { personArray[i] = p; }
// ------------------
   public person getp(int i)     // get person at index
      { return personArray[i]; }
// ------------------
   public void clear()           // empty node of persons
      {
      for(int j=0; j<ORDER-1; j++)
         personArray[j] = null;
      numPers = 0;
      }
// ------------------
   public boolean isFull()
      { return (numPers==ORDER-1) ? true : false; }
// -------------------------------------------------------------
   public int findItem(double key)         // return index of
      {                                    // item (within node)
      for(int j=0; j<ORDER-1; j++)         // if found,
         {                                 // otherwise,
         if(personArray[j] == null)          // return -1
            break;
         else if(personArray[j].getHeight() == key)
            return j;
         }
      return -1;
      }  // end findItem
// -------------------------------------------------------------
   public void insertPers(person p)
      {
      // assumes node is not full
      int j;
      if(numPers==0)               // if empty,
         {                         // insert
         personArray[0] = p;       // new person
         numPers++;
         return;
         }
      int ourHeight = p.getHeight();
      for(j=0; j<numPers; j++)     // for each person
         {                         //    in node
         int itsHeight = getp(j).getHeight();
         if(ourHeight < itsHeight) // if we're less,
            {                                 // move following
            for(int k=numPers-1; k >= j; k--) // persons
               personArray[k+1] = personArray[k];
            personArray[j] = p;    // insert new one
            numPers++;
            return;
            }
         // so if we're greater, keep looking
         }
      personArray[j] = p;          // we're the biggest
      numPers++;
      }  // end insertPers()
// ------------------
   public boolean areWeCurrentNode()
      { return weAreCurrentNode; }
// ------------------
   public void setCurrentNode(boolean b)
      { weAreCurrentNode = b; }
// ------------------
   }  // end class node
///////////////////////
class nodeGroup
   {
   private final int appletWidth = 440;
   private final int appletHeight = 300;
   private final int topMargin = 70;
   private final int leftMargin = 10;
   private final int zoomLeftMargin = 30; // for zoom-in view
   private final int textHeight = 13;
   private final int digits3Width = 13;
   private final int hF1 = 10;   // fudge factors to position
   private final int hF2 = 7;    // numbers within nodes
   private final int hF3 = 4;
   private final int vF = 8;
   private final int nodeWidth = 80;
   private final int nodeHeight = 25;
   private final int nodeArcDiam = 15;
   private final int personWidth = nodeWidth/3;
   private final int horizSeparation = nodeWidth + 25;
   private final int levelSeparation = 60;
   private final int noteBoxTop = 45;
   private final int noteBoxHeight = 25;
   private final int noteBoxWidth = 300;
   private final int smallAppletWidth = 384;
   private final int smallNodeWidth = 4;
   private final int smallNodeHeight = 6;
   private final int ASIZE = 85;  // maximum nodes in tree
   private final int MAX_KEY = 999;

   private node root = new node();
   private node nodeArray[];      // array for holding nodes
   private String note;           // displayed on screen
   private int value;             // value entered by user
   private int codePart = 1;      // which part of sequence?
   private int codePart2 = 1;     //    for fill
   private int opMode;            // 1=Fill, 2=Ins, etc.
   private node curNo;            // current node
   private int lev1View = 0;      // parent nodes of next level
   private int lev2View = 0;      //    to display (0 to 3)
   private boolean usedLowestLevel = false;
   private boolean zoomIn = true; // zoomed out if false
   private person tempPers;       // temporary person for insert
   private int start1;            // 1st of 4 visible nodes
   private int start2;            // same in level 2
   private int oldStart1, oldStart2;
   private int curIn;      // index of node with arrow
   private int oldCurIn;
   private boolean viewSetByMouse = true;
   private int drawMode;          // 1 = one node, 2 = all nodes
   private int utilNumber;        // for find()
// ------------------
   public nodeGroup()               // constructor
      {
      nodeArray = new node[ASIZE];  // array for tree
      note = "Press a button to start";
      curNo = root;
      curNo.setCurrentNode(true);
      }  // end constructor
// ------------------
   public void toggleZoom()
      {
      drawMode = 2;
      zoomIn = (zoomIn==true) ? false : true;
      }
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
   public void setView(int x, int y)    // sets viewable nodes
      {
      if(zoomIn==false)
         return;
      drawMode = 2;
      int level = (y-topMargin) / levelSeparation;
      int column = (x-leftMargin) / horizSeparation;

      if(level==1)
         lev1View = column;
      if(level==2)
         lev2View = column;
      viewSetByMouse = true;  // mouse click determines
      }                       // which nodes will be viewed
// ------------------
   public void fill(boolean isNumb, int insVal)
      {
      if(zoomIn==false)       // not while zoomed out
         return;
      if(opMode==3 && codePart != 1)  // not while inserting
         return;
      if(opMode != 1)
         {
         opMode = 1;
         codePart2 = 1;
         }
      switch(codePart2)
         {
         case 1:
            note = "Enter number of items to fill in";
            curNo.setCurrentNode(false);
            curNo = root;
            curNo.setCurrentNode(true);
            drawMode = 1;
            codePart2 = 2;
            break;
         case 2:
            if(isNumb != true || insVal < 0 || insVal > 45)
               {
               note = "ERROR: use number between 0 and 45";
               drawMode = 1;
               codePart2 = 1;
               }
            else
               {
               doFill(insVal);
               opMode = 1;
               note = "Fill completed";
               drawMode = 2;
               codePart2 = 6;
               }
            break;
          case 6:
            note = "Press any button";
            drawMode = 1;
            codePart2 = 1;
            break;
         }  // end switch
      }  // end fill
// ------------------
   public void doFill(int numPersons)
      {
      root = new node();         // completely new tree
      usedLowestLevel = false;
      for(int j=0; j<numPersons; j++)
         {
         insert( true, 1000 );    // codePart: 1
         insert( true,            // codePart: 2
              (int)(java.lang.Math.random()*MAX_KEY) );
         while(codePart != 1)
            insert( true, 1000 ); // 3, 3, 3, ..., 3, 5, 6, 1
         }
      }
// ------------------
   // find a person
   public void find(boolean isNumb, int insVal)
      {
      if(zoomIn==false)
         return;
      if(opMode != 2)
         {
         opMode = 2;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            note = "Enter value of item to find";
            curNo.setCurrentNode(false);
            curNo = root;
            curNo.setCurrentNode(true);
            drawMode = 1;
            codePart = 2;
            break;
         case 2:
            if(!isNumb || insVal < 0 || insVal > MAX_KEY)
               {
               note = "Items have values from 0 to " + MAX_KEY;
               codePart = 1;      // inappropriate node number
               }
            else
               {
               value = insVal;
               note = "Will find item with value " + value;
               codePart = 3;
               }
            drawMode = 1;
            break;
         case 3:                  // item in this node?
            if( (utilNumber=curNo.findItem(value)) != -1 )
               {
               note = "Found item; number " + utilNumber +
                      " in this node";
               viewSetByMouse = false;
               drawMode = 1;
               codePart = 5;
               break;
               }
            else if( curNo.isLeaf() )      // node is leaf?
               {
               note = "Can't find item";
               viewSetByMouse = false;
               drawMode = 1;
               codePart = 5;
               break;
               }
            else // item not in this node, node not a leaf
               {
               curNo.setCurrentNode(false);    // search for node
               curNo = getNextChild(curNo, value);
               curNo.setCurrentNode(true);
               note = "Went to child number " + utilNumber;
               viewSetByMouse = false;
               drawMode = 1;
               codePart = 3;
               break;
               }
         // no case 4
         case 5:
            note = "Search completed";
            drawMode = 1;
            codePart = 6;
            break;
         case 6:
            note = "Press any button";
            drawMode = 1;
            codePart = 1;
            break;
         }  // end switch
      }  // end find()
// ------------------
   // insert a person
   public void insert(boolean isNumb, int insVal)
      {
      if(zoomIn==false)
         return;
      if(opMode != 3)
         {
         opMode = 3;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            note = "Enter value of item to insert";
            curNo.setCurrentNode(false);
            curNo = root;
            curNo.setCurrentNode(true);
            drawMode = 1;
            codePart = 2;
            break;
         case 2:
            if(!isNumb || insVal < 0 || insVal > MAX_KEY)
               {
               note = "Items have values from 0 to " + MAX_KEY;
               codePart = 1;      // inappropriate node number
               }
            else
               {
               value = insVal;
                                  // make person to insert
               tempPers = makePerson(value);
               note = "Will insert item with value " + value;
               codePart = 3;
               }
            drawMode = 1;
            break;
         case 3:
            if( curNo.isFull() )  // if node is full,
               {
               int result = split(curNo);  // split it
               if(result != -1)
                  note = "Node was split";
               else               // error return
                  {
                  note = "Tree depth too great, CAN'T INSERT";
                  curNo.setCurrentNode(false);
                  curNo = root;
                  curNo.setCurrentNode(true);
                  drawMode = 1;
                  codePart = 6;
                  break;
                  }
               if(curNo != root)             // if not root,
                  {
                  curNo.setCurrentNode(false);
                  curNo = curNo.getParent(); // back up
                  curNo.setCurrentNode(true);
                  }
               curNo.setCurrentNode(false);
               curNo = getNextChild(curNo, value); // search once
               curNo.setCurrentNode(true);
               viewSetByMouse = false;
               drawMode = 2;
               codePart = 3;
               break;
               }  // end if(node is full)

            if( curNo.isLeaf() )            // if node is leaf,
               {                            // insert new person
               curNo.insertPers(tempPers);
               note = "Inserted new item in leaf";
               viewSetByMouse = false;
               drawMode = 1;
               codePart = 5;
               break;
               }

            // otherwise, node is not full, not a leaf
            curNo.setCurrentNode(false);    // search for node
            curNo = getNextChild(curNo, value);
            curNo.setCurrentNode(true);
            note = "Searching for insertion point";
            viewSetByMouse = false;
            drawMode = 1;
            codePart = 3;
            break;
         // no case 4
         case 5:
            note = "Insertion completed";
            drawMode = 1;
            codePart = 6;
            break;
         case 6:
            note = "Press any button";
            drawMode = 1;
            codePart = 1;
            break;
         }  // end switch
      }  // end insert()
// ------------------
   public int split(node theNode)     // split the node
      {
      int j;
                                 // save node's persons
      person p0 = theNode.getp(0);
      person p1 = theNode.getp(1);
      person p2 = theNode.getp(2);
                                 // save node's children
      node ch0 = theNode.getChild(0);
      node ch1 = theNode.getChild(1);
      node ch2 = theNode.getChild(2);
      node ch3 = theNode.getChild(3);

      if(theNode==root)          // if it's the root
         {
         if(usedLowestLevel)     // if any node on lowest level,
            return -1;           //    can't split root
         root.clear();           // clear persons from node
                                 // make 2 new child nodes
         node newLeftChild = new node();
         root.connectChild(0, newLeftChild);
         node newRightChild = new node();
         root.connectChild(1, newRightChild);
                                 // insert persons in 3 nodes
         newLeftChild.insertPers(p0);
         root.insertPers(p1);
         newRightChild.insertPers(p2);
                                 // connect root to children
         root.connectChild(0, newLeftChild);
         root.connectChild(1, newRightChild);
         root.connectChild(2, null);
         root.connectChild(3, null);

         if(ch0 != null)         // connect
            {                    // children to grandchildren
            newLeftChild.connectChild(0, ch0);
            if(ch1 != null)
               {
               newLeftChild.connectChild(1, ch1);
               if(ch2 != null)
                  {
                  newRightChild.connectChild(0, ch2);
                  if(ch3 != null)
                     {
                     newRightChild.connectChild(1, ch3);
                     }  // end if(ch3...
                  }  // end if(ch2...
               }  // end if(ch1...
            }  // end if(ch0...
         }  // end if(node is root)
      else                       // it's not the root
         {
         int ourChildNumber = theNode.getChildNumber(); // child #
         node parent = theNode.getParent();      // get parent
         int numSibs = parent.getNumPers() + 1;  // # of siblings
         // for all siblings on our right,
         // move parent's connections to the right one child
         for(j=numSibs-1; j>ourChildNumber; j--)
            {
            node temp = parent.getChild(j);
            parent.connectChild(j+1, temp);
            }
         // make a new node, insert to our immediate right
         node newRight = new node();
         parent.connectChild(ourChildNumber+1, newRight);

         theNode.clear();         // clear this node
         theNode.insertPers(p0);  // p0 into this
         parent.insertPers(p1);   // p1 into parent
         newRight.insertPers(p2); // p2 into new right

         // move theNode's ch2 $ ch3 to newRight's ch0 & ch1
         if(ch2 != null)
            {
            newRight.connectChild(0, ch2);
            theNode.connectChild(2, null);
            if(ch3 != null)
               {
               newRight.connectChild(1, ch3);
               theNode.connectChild(3, null);
               }
            }
         }
      return 0;  // successful return
      }  // end split()
// ------------------
   // gets appropriate child of nodeDex during search for value
   public node getNextChild(node theNode, int theValue)
      {
      int j;
      // assumes node is not empty, not full, not a leaf
      int numPers = theNode.getNumPers();
      for(j=0; j<numPers; j++)       // for each person in node
         {                               // are we less?
         if( theValue < theNode.getp(j).getHeight() )
            {
            utilNumber = j;
            return theNode.getChild(j);  // return left child
            }
         }  // end for
                                         // we're greater, so
      utilNumber = j;
      return theNode.getChild(j);        // return right child
      }
// ------------------
   public void drawOneNode(Graphics g, int nodeDex)
      {
      if(nodeArray[nodeDex]==null)
         return;
      int column, level, x, y;
      int parentX, parentY, parentColumn, xIncr=0;
      column = (nodeDex-1)%4;

      if(nodeDex==0) level = 0;
      else if(nodeDex>0 && nodeDex<5) level = 1;
      else if(nodeDex>4 && nodeDex<21) level = 2;
      else level = 3;

      if(level==0)                      // find our coordinates
         x = leftMargin + (3*horizSeparation)/2;
      else
         x = leftMargin + column*horizSeparation;
      y = topMargin + level*levelSeparation;

      drawPerson(g, x, y, nodeDex, 0);  // left person
      drawPerson(g, x, y, nodeDex, 2);  // right person
      drawPerson(g, x, y, nodeDex, 1);  // middle person
      // (1 must be last)

      g.setColor(Color.lightGray);      // erase old node number
      g.fillRect(x+nodeWidth+2, y, digits3Width, textHeight);
      g.setColor(Color.black);          // draw node number
      g.drawString(""+nodeDex, x+nodeWidth+2, y+nodeHeight/2);

      g.drawLine(x+personWidth+1, y,    // draw lines between
                 x+personWidth+1, y+nodeHeight);  // persons
      g.drawLine(x+2*personWidth+2, y,            // within node
                 x+2*personWidth+2, y+nodeHeight);
                                        // draw node outline
      g.drawRoundRect(x, y, nodeWidth, nodeHeight,
                      nodeArcDiam, nodeArcDiam);
                                        // if we are current node
      if( nodeArray[nodeDex].areWeCurrentNode() )
         g.setColor(Color.red);         // red arrow
      else                              // all other nodes
         g.setColor(Color.lightGray);   //    gray arrow
      int xTop = x + nodeWidth/2;    // draw arrow
      g.drawLine(xTop,   y-1, xTop,   y-20);  // shaft
      g.drawLine(xTop-1, y-1, xTop-1, y-20);
      g.drawLine(xTop,   y-1, xTop-3, y-7);   // left feather
      g.drawLine(xTop-1, y-1, xTop-4, y-7);
      g.drawLine(xTop,   y-1, xTop+3, y-7);   // right feather
      g.drawLine(xTop-1, y-1, xTop+2, y-7);

      // draw a small blue triangle for each of node's children
      for(int j=0; j<4; j++)            // for each child,
         {
         if(nodeArray[nodeDex].getChild(j) != null)
            {                           // if it exists
            int xCh=x;
            switch(j)
               {
               case 0: xCh = x + nodeArcDiam/2; break;
               case 1: xCh = x +   personWidth+1; break;
               case 2: xCh = x + 2*personWidth+2; break;
               case 3: xCh = x + nodeWidth - nodeArcDiam/2; break;
               }
            g.setColor(Color.blue);     // make triangle from
            for(int k=0; k<5; k++)      // series of lines
               g.drawLine(xCh-k, y+nodeHeight-4+k,
                          xCh+k, y+nodeHeight-4+k);
            }  // end if(nodeArray)
         else
            break;
         }  // end for(j)

// TEST check that we are really our parent's child
      if(nodeDex != 0)
         {
         node ourParent = nodeArray[nodeDex].getParent();
         int ourChildNumber = nodeArray[nodeDex].getChildNumber();
         node shouldBeUs = ourParent.getChild(ourChildNumber);
         if(shouldBeUs != nodeArray[nodeDex])
            {
            note = "ERROR: parent wrong in node " + nodeDex;
            g.setColor(Color.black);       // draw line thru node
            g.drawLine(x, y, x+nodeWidth, y+nodeHeight);
            g.drawLine(x, y+1, x+nodeWidth, y+nodeHeight+1);
            g.drawLine(x, y+2, x+nodeWidth, y+nodeHeight+2);
            }
         }
// END TEST

      if(nodeDex==0)                    // if we're the root,
         return;                        //    no line above us
      int myParent = (nodeDex-1)/4;     // draw line to parent
      g.setColor(Color.black);
      switch(column)
         {
         case 0: xIncr = nodeArcDiam/2; break;
         case 1: xIncr = personWidth+1; break;
         case 2: xIncr = 2*(personWidth+1); break;
         case 3: xIncr = nodeWidth-nodeArcDiam/2; break;
         }
      if(myParent==0)                   // root
         parentX = leftMargin + (3*horizSeparation)/2 + xIncr;
      else                              // non-root
         {
         parentColumn = (myParent-1)%4;
         parentX = leftMargin +
                   parentColumn*horizSeparation + xIncr;
         }
      parentY = y-levelSeparation + nodeHeight;
      g.drawLine(x+nodeWidth/2, y, parentX, parentY);
      }  // end drawOneNode()
// ------------------
 public void drawPerson(Graphics g, int x, int y,
                        int nodeDex, int persDex)
   {
   int hF, height;
   Color c;
                                   // if no person here,
   if(nodeArray[nodeDex].getp(persDex)==null)
      {
      height = -9999;              // invalid number
      c = Color.lightGray;         // background color
      }
   else
      {
      height = nodeArray[nodeDex].getp(persDex).getHeight();
      c = nodeArray[nodeDex].getp(persDex).getColor();
      }
   g.setColor(c);
                                   // x different for right pers
   int newX = (persDex==2) ? x+nodeWidth/2 : x;
                                   // draw colored shape
   if(persDex==1)                  // middle person not rounded
      g.fillRect(x+personWidth+1, y, personWidth+2, nodeHeight);
   else                            // end persons are rounded
      g.fillRoundRect(newX, y, nodeWidth/2, nodeHeight,
                      nodeArcDiam, nodeArcDiam);
   if(height<10) hF = hF1;         // fudge factors for digits
   else if(height<100) hF = hF2;
   else hF = hF3;
   if(height != -9999)             // unless no person,
      {
      g.setColor(Color.black);     // draw height number
      g.drawString(""+height, x + hF + persDex*personWidth,
                              y + nodeHeight - vF);
      }
   }
// ------------------
   // transfers node tree to nodeArray for display; recursive
   public void transfer(node theNode, int theIndex)
      {
      if(theIndex > 20)                 // remember if node
         usedLowestLevel = true;        //    on bottom row
      if( theNode.areWeCurrentNode() )  // establish current
         curIn = theIndex;       //    index
      nodeArray[theIndex] = theNode;    // transfer the node
      if( theNode.isLeaf() )
         return;
      for(int j=0; j<4; j++)                   // transfer
         {                                     // the node's
         node theChild = theNode.getChild(j);  // children
         if(theChild != null)                  // by calling
            {                                  // ourself
            int theChildIndex = theIndex*4 + j + 1;
            transfer(theChild, theChildIndex);
            }
         else
            break;
         }  // end for
      }  // end transfer()
// ------------------
   public void draw(Graphics g)      // draw tree
      {
      int j, x, y;
      for(j=0; j<ASIZE; j++)         // clear node array
         nodeArray[j] = null;
      transfer(root, 0); // put tree into nodeArray for display

      if(viewSetByMouse)             // mouse determines view
         {
         start1 = 5 + lev1View*4;    // find left-most indices
         start2 = 21 + lev1View*16 + lev2View*4;
         }
      else                           // current index
         {                           // determines view
         if(curIn>0 && curIn<5)
            {
            if( nodeArray[start1] != null &&
                nodeArray[start1].getParent() !=
                                            nodeArray[curIn] )
               start1 = curIn*4 + 1;    // 1st child
            if(nodeArray[start2] != null &&
               nodeArray[start1] != null)
               {
               node ps2 = nodeArray[start2].getParent();
               if(ps2 != null)
                  {
                  node pps2 = ps2.getParent();
                  if(pps2 != nodeArray[curIn] )
                     start2 = start1*4 + 1;   // 1st ch of 1st ch
                  }
               }
            }
         else if(curIn>4 && curIn<21)
            {
            start1 = ((curIn-5)/4)*4 + 5;
            start2 = curIn*4 + 1;    // 1st child
            }
         else if(curIn>20 && curIn<85)
            {
            start1 = ((curIn-21)/16)*4 + 5;
            start2 = ((curIn-21)/4)*4 + 21;
            }
         }
      if(oldStart1 != start1 ||         // if view has changed
          (oldStart2 != start2 && usedLowestLevel) )
         drawMode = 2;
      oldStart1 = start1;
      oldStart2 = start2;

      if(drawMode==1)                   // draw only one node
         {
         g.setColor(Color.lightGray);   // clear text area
         g.fillRect(leftMargin, noteBoxTop, noteBoxWidth,
                    noteBoxHeight);
         g.setColor(Color.black);       // draw 'note'
         g.drawString(note, leftMargin+6,
                      noteBoxTop+textHeight+6);

         if(oldCurIn<5 ||
            (oldCurIn>4 && oldCurIn<21 && oldCurIn-start1<4
                                       && oldCurIn-start1>=0) ||
            (oldCurIn>20 && oldCurIn<85 && oldCurIn-start2<4
                                        && oldCurIn-start2>=0) )
            drawOneNode(g, oldCurIn);   // (to erase arrow)
         if( curIn<5 ||
             (curIn>4 && curIn<21 && curIn-start1<4
                                  && curIn-start1>=0) ||
             (curIn>20 && curIn<85 && curIn-start2<4
                                   && curIn-start2>=0) )
            drawOneNode(g, curIn);      // draw current node
         drawMode = 2;
         }
      else                              // draw all nodes
         {
         int yTop = topMargin+nodeHeight+1;

         g.setColor(Color.lightGray);   // clear entire screen
         g.fillRect(0, 0, appletWidth, appletHeight);

         if(zoomIn==false)              // zoom out; big picture
            {
            drawSmall(g, 0, 0, -1, -1); // draw all small nodes

            boxAndText(g, Color.green, 0,
               "Node exists and is visible in closeup view");
            boxAndText(g, Color.magenta, 15,
               "Node exists but is not visible");
            boxAndText(g, Color.gray, 30,
               "Node does not exist");
             }
         else                           // zoomed in; big nodes
            {
            if(nodeArray[0] != null)             // node 0
               drawOneNode(g, 0);
            for(j=0; j<4; j++)
               {
               if(nodeArray[j+1] != null)        // nodes 1-4
                  drawOneNode(g, j+1);
               if(nodeArray[start1+j] != null)   // 4 of nodes 5-20
                  drawOneNode(g, start1+j);
               if(nodeArray[start2+j] != null)   // 4 of nodes 21-84
                  drawOneNode(g, start2+j);
               }
            g.setColor(Color.black);          // draw text ('note')
            g.drawString(note, leftMargin+6,
                         noteBoxTop+textHeight+6);
            }  // end else(zoomed in)
         }  // end else drawMode is 2
      oldCurIn = curIn;
      }  // end draw()
// ------------------
   public void boxAndText(Graphics g, Color c, int y, String s)
      {
      g.setColor(c);
      g.fillRect(leftMargin, y+topMargin-smallNodeHeight-10,
                 smallNodeWidth, smallNodeHeight);
      g.setColor(Color.black);
      g.drawString(s, leftMargin+10, y+topMargin-10);
      }
// ------------------
   // recursive; calls itself to draw all 85 small nodes
   public void drawSmall(Graphics g, int level,
                         int nodeDex, int px,  int py)
      {
      int x = zoomLeftMargin;
      int y, j=nodeDex;
      int aw=smallAppletWidth, aw4=aw/4, aw16=aw/16, aw64=aw/64;
      int ls = levelSeparation;
      int tm = topMargin + 15;

      if(level==0)                           // find our coords
         { x += aw/2;                 y = tm; }
      else if(level==1)
         { x += aw4/2 + aw4*(j-1);    y = tm + 1*ls; }
      else if(level==2)
         { x += aw16/2 + aw16*(j-5);  y = tm + 2*ls; }
      else if(level==3)
         { x += aw64/2 + aw64*(j-21); y = tm + 3*ls; }
      else
         { x = -1; y = -1; }                 // error

      g.setColor(Color.gray);                // node outline
      g.drawRect(x, y, smallNodeWidth, smallNodeHeight);

      if(nodeDex != 0)                       // line to parent
         g.drawLine(x+smallNodeWidth/2, y,
                    px+smallNodeWidth/2, py+smallNodeHeight);

      if(nodeArray[j]==null)                 // null node: gray
         g.setColor(Color.gray);
      else if( (j>=start1 && j<start1+4) ||  // visible
               (j>=start2 && j<start2+4) ||  // in zoomOut
               j < 5 )                       // mode: green
         g.setColor(Color.green);
      else                                   // not
         g.setColor(Color.magenta);          // visible: magenta
      g.fillRect(x, y, smallNodeWidth, smallNodeHeight);

      if(level < 3)                          // if not lowest
         for(int k=0; k<4; k++)              // draw each child
            drawSmall(g, level+1, nodeDex*4+k+1, x, y);
      }  // end drawSmall()
// ------------------
   }  // end class nodeGroup
////////////////////////////
public class Tree234 extends java.applet.Applet
                     implements Runnable, ActionListener,
                                MouseListener
   {
   private Thread runner;
   private nodeGroup theNodeGroup;
   private int GPNumber = -1;      // general-purpose number
   private boolean isNumber = false;  // is GPNumber valid
   private TextField tf = new TextField("", 4);
   private Button fillButton, findButton, insButton, zoomButton;
// ------------------
   public void init()
      {
      addMouseListener(this);

      setLayout( new FlowLayout() );
      Panel p1 = new Panel();
      add(p1);
      p1.setLayout( new FlowLayout() );

      Panel p2 = new Panel();
      p1.add(p2);
      p2.setLayout( new FlowLayout(FlowLayout.LEFT) );

      fillButton = new Button("Fill");     // Fill button
      p2.add(fillButton);
      fillButton.addActionListener(this);

      findButton = new Button("Find");     // Find button
      p2.add(findButton);
      findButton.addActionListener(this);

      insButton = new Button("Ins");       // Ins button
      p2.add(insButton);
      insButton.addActionListener(this);

      zoomButton = new Button("Zoom");     // Zoom button
      p2.add(zoomButton);
      zoomButton.addActionListener(this);

      Panel p3 = new Panel();
      p1.add(p3);
      p3.setLayout( new  FlowLayout(FlowLayout.RIGHT) );
      p3.add( new Label("Enter number: ") );
      p3.add(tf);
      theNodeGroup = new nodeGroup();  // start with tree
      theNodeGroup.doFill(10);         // with 10 items
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
      { theNodeGroup.draw(gg); }
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
      if(event.getSource() == fillButton)      // "Fill" button?
         theNodeGroup.fill(isNumber, GPNumber);
      else if(event.getSource() == findButton) // "Find" button?
         theNodeGroup.find(isNumber, GPNumber);
      else if(event.getSource() == insButton)  // "Ins" button?
         theNodeGroup.insert(isNumber, GPNumber);
      else if(event.getSource() == zoomButton) // "Zoom" button?
         theNodeGroup.toggleZoom();

      repaint();                        // all buttons
      try{ Thread.sleep(10); }
      catch(InterruptedException e)
          {  }
      }  // end action
// ------------------
   public void run()
      {
      while(true)
         {
         }
      }  // end run()
// ------------------
   public void mousePressed(MouseEvent event)
      {
      int x = event.getX();
      int y = event.getY();

      if(event.getClickCount() == 1)
         {
         theNodeGroup.setView(x, y);
         repaint();
         }
      }  // end mousePressed()
// ------------------
   public void mouseReleased(MouseEvent e)
      {  }
// ------------------
   public void mouseEntered(MouseEvent e)
      {  }
// ------------------
   public void mouseExited(MouseEvent e)
      {  }
// ------------------
   public void mouseClicked(MouseEvent e)
      {  }
// ------------------
   }  // end class Tree234
//////////////////////////


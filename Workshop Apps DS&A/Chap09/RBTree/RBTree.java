// RBTree.java
// demonstrates Red-Black binary tree
import java.awt.*;
import java.awt.event.*;
////////////////////////////////////////////////////////////////
class person
   {
   private int height;           // person height
   private Color color;          // person color
   private boolean red;          // red (true) or black node
   private int mark;             // choice-point marks
                                 //    0 = not visited
                                 //    1 = go left
                                 //    2 = go right
   public Color getColor()       // access color
      { return color; }

   public int getHeight()        // access height
      { return height; }

   public void setRed(boolean r)
      { red = r; }

   public boolean getRed()
      { return red; }

   public int getMark()
      { return mark; }

   public void setMark(int m)
      { mark = m; }

   public person(int h, Color c) // constructor
      {
      height = h;
      color = c;
      red = true;
      mark = 0;     // not visited
      }
   }
/////////////////////////////////////////////////////////////////
// tree of person objects is stored in treeArray
// index of array elements corresponds to top-to-bottom
// left-to-right numbering of tree nodes, from 0 on top
// to 30 on the lower right (a maximum of 31 possible nodes)
// parent=(index-1)/2, leftChild=2*index+1, rightChild=2*index+2
class personGroup
   {
   private final int appletWidth = 440;
   private final int appletHeight = 300;
   private final int maxHeight = 200;
   private final int topMargin = 90;
   private final int leftMargin = 10;
   private final int textHeight = 13;
   private final int nodeDiameter = 20;
   private final int levelSeparation = 40;
   private final int horizSeparation = nodeDiameter + 6;
   private final int noteBoxTop = 45;
   private final int noteBoxHeight = 25;
   private final int noteBoxWidth = 300;
   private final int visitBoxTop = 280;
   private final int visitBoxHeight = 25;
   private final int visitBoxWidth = 430;
   private final int ASIZE = 31;  // maximum size of tree
   private final int MAX_KEY = 99;

   private person treeArray[];    // array for holding persons
   private String note;           // displayed on screen
   private boolean isRand = true; // random or user-entered?
   private int value;             // value entered by user
   private int codePart = 1;      // which part of sequence?
   private int opMode;            // 1=Fill, 2=Find, 3=Ins, etc.
   private int curIn;             // current index
   private int curInOld;          // previous current index
   private int oldArrow;          // old arrow location
// ***for debugging***
//   private int visitArray[];      // holds 'visited' values
//   private int visitIndex;        // index to visited values
   private int successor = 0;     // next-larger key value
   private boolean drawAll;       // draw all nodes or not
   private int drawMode = 2;      // draw: 0 = no nodes
                                  //    1 = 1 node (& ancestors)
                                  //    2 = all nodes
//--------------------------------------------------------------
   public personGroup()              // constructor
      {
      treeArray = new person[ASIZE]; // array for tree
      for(int j=0; j<ASIZE; j++)
         treeArray[j] = null;        // fill with null objects
      note = "Press a button, or click on a node";
      curIn = curInOld = 0;          // arrow at top
  //    visitArray = new int[200];     // array for 'visits'
  //    visitIndex = 0;
      }  // end constructor
//--------------------------------------------------------------
                                  // return a person
   public person makePerson(int height)
      {                           // of specified height and
                                  //    random RGB color
      int red = 100 + (int)(java.lang.Math.random()*154);
      int green = 100 + (int)(java.lang.Math.random()*154);
      int blue = 100 + (int)(java.lang.Math.random()*154);
      Color newColor = new Color(red, green, blue);
      return new person(height, newColor);
      }  // end makePerson()
//--------------------------------------------------------------
   public void drawOneNode(Graphics g, int index)
      {
      if(treeArray[index]==null)
         return;
      int height = treeArray[index].getHeight();
      Color c = treeArray[index].getColor();
      boolean itsRed = treeArray[index].getRed();
      int hand = index % 2;          // 0=I'm right, 1=I'm left
      int column = 15;               // calculate location
      int level = 0;                 // index is 0
      int parentColumn = -1;
      if(index>0 && index<3)         // index is 1 to 2
         {
         column = 7 + (index-1)*16;
         level = 1;
         parentColumn = (hand==1) ? column+8 : column-8;
         }
      else if(index>2 && index<7)    // index is 3 to 6
         {
         column = 3 + (index-3)*8;
         level = 2;
         parentColumn = (hand==1) ? column+4 : column-4;
         }
      else if(index>6 && index<15)   // index is 7 to 14
         {
         column = 1 + (index-7)*4;
         level = 3;
         parentColumn = (hand==1) ? column+2 : column-2;
         }
      else if(index>14 && index<31)  // index is 15 to 30
         {
         column =     (index-15)*2;
         level = 4;
         parentColumn = (hand==1) ? column+1 : column-1;
         }
                                     // our coordinates
      int x = leftMargin + column*horizSeparation/2;
      int y = topMargin + level*levelSeparation;
                                     // get parent's coords
      int xP = leftMargin + parentColumn*horizSeparation/2;
      int yP = topMargin + (level-1)*levelSeparation;

      if(level>0)                    // unless we're the root,
         {                           // draw line to parent
         g.setColor(Color.black);
         g.drawLine(x+nodeDiameter/2, y+nodeDiameter/2,
                    xP+nodeDiameter/2, yP+nodeDiameter/2);
         }
      g.setColor(c);                 // fill the circle
      g.fillOval(x, y, nodeDiameter, nodeDiameter);
      if(itsRed==false)              // set border color
         g.setColor(Color.black);
      else
         g.setColor(Color.red);      // double-width border
      g.drawOval(x, y, nodeDiameter, nodeDiameter);
      g.drawOval(x-1, y-1, nodeDiameter+2, nodeDiameter+2);

      g.setColor(Color.black);
      if(height < 10)                // draw height number
         g.drawString(""+height, x+7, y+nodeDiameter-5);
      else
         g.drawString(""+height, x+4, y+nodeDiameter-5);
      }  // end drawOneNode()
//--------------------------------------------------------------
   public void draw(Graphics g)      // draw the tree
      {
      int tempDrawMode;
                                     // draw all nodes?
      tempDrawMode = (drawAll==true) ? 2 : drawMode;
      switch(tempDrawMode)
         {
         case 0:                     // draw no nodes
            break;
         case 1:                     // draw current & ancestors
            int tempDex = curInOld;  // find parent
            while(tempDex > 0) // doesn't redraw root
               {
               drawOneNode(g, tempDex);  // draw node
               tempDex = (tempDex-1)/2;  // get node's parent
               }
            drawOneNode(g, 0);       // draw root
            break;
         case 2:                     // draw all nodes
            g.setColor(Color.lightGray);   // clear applet screen
            g.fillRect(0, 0, appletWidth, appletHeight);

            for(int j=ASIZE-1; j>=0; j--)  // draw all nodes
               drawOneNode(g, j);          // in reverse order
            break;                         // (to handle lines)
         }  // end switch

      g.setColor(Color.lightGray);      // clear upper text area
      g.fillRect(leftMargin, noteBoxTop, noteBoxWidth,
                 noteBoxHeight);
      g.setColor(Color.black);          // draw text ('note')
      g.drawString(note, leftMargin+6,
                   noteBoxTop+textHeight+6);

  //    g.setColor(Color.lightGray);      // clear lower text area
  //    g.fillRect(leftMargin, visitBoxTop,
  //               visitBoxWidth, visitBoxHeight );
      g.setColor(Color.black);          // in lower text area,
      String s = "";                    // draw nodes visited
   //   for(int j=0; j<visitIndex; j++)   // (for debugging ******)
   //      s += (visitArray[j]+" ");
      g.drawString(s, leftMargin+6,
                   visitBoxTop+textHeight+3);
      drawArrow(g, oldArrow, false);    // erase old arrow
      drawArrow(g, curInOld, true);     // draw new arrow
                                        // next time, unless
      drawAll = true;                   //    button push, draw
      }  // end draw()                  //    all the nodes
//--------------------------------------------------------------
   public void drawArrow(Graphics g, int index, boolean draw)
      {
      if(treeArray[index]==null)
         return;
      int column = 15;               // calculate location
      int level = 0;                 // index is 0
      if(index>0 && index<3)         // index is 1 to 2
         {
         column = 7 + (index-1)*16;
         level = 1;
         }
      else if(index>2 && index<7)    // index is 3 to 6
         {
         column = 3 + (index-3)*8;
         level = 2;
         }
      else if(index>6 && index<15)   // index is 7 to 14
         {
         column = 1 + (index-7)*4;
         level = 3;
         }
      else if(index>14 && index<31)  // index is 15 to 30
         {
         column =     (index-15)*2;
         level = 4;
         }
                                     // our coordinates
      int x = leftMargin + column*horizSeparation/2;
      int y = topMargin + level*levelSeparation;

      if(draw==true)                 // draw the arrow
         g.setColor(Color.red);
      else                           // erase the arrow
         g.setColor(Color.lightGray);
      int xTop = x + nodeDiameter/2;
      int yTop = y - 2;
      int alen = levelSeparation/2;
      g.drawLine(xTop,   yTop, xTop,   yTop-alen);  // shaft
      g.drawLine(xTop-1, yTop, xTop-1, yTop-alen);
      g.drawLine(xTop,   yTop, xTop-3, yTop-6); // left feather
      g.drawLine(xTop-1, yTop, xTop-4, yTop-6);
      g.drawLine(xTop,   yTop, xTop+3, yTop-6); // right feather
      g.drawLine(xTop-1, yTop, xTop+2, yTop-6);
      }  // end drawArrow()
//--------------------------------------------------------------
   public void setDrawAll(boolean da)
      {                       // set by Tree, used by draw()
      drawAll = da;           // true = draw all nodes
      }                       // false = use drawMode value
//--------------------------------------------------------------
   // puts one person at root
   public void fillRoot()
      {
      for(int j=0; j<ASIZE; j++)      // fill entire tree
         treeArray[j] = null;         // with null objects

      treeArray[0] = makePerson(50);  // put (50) in root
      treeArray[0].setRed(false);     // make it black
      curIn = curInOld = 0;           // arrow at root
      drawAll = true;                 // redraw all nodes
      check();                        // check r/b correctness
      }
//--------------------------------------------------------------
   public void quickInsert(boolean isNumb, int insVal)
      {
//      visitIndex = 0;
      if(!isNumb || insVal < 0 || insVal > MAX_KEY)
         {
         note = "Nodes have values from 0 to 99";
         return;
         }
      curIn = 0;                  // start at root
      while(treeArray[curIn] != null)
         {                        // if two red children,
         if(curIn<15 &&           // needs color flip
            treeArray[2*curIn+1] != null &&
            treeArray[2*curIn+2] != null &&
            treeArray[curIn].getRed()== false &&
            treeArray[2*curIn+1].getRed()== true &&
            treeArray[2*curIn+2].getRed()== true)
            {
            oldArrow = curInOld;
            curInOld = curIn;
            note = "CAN'T INSERT: needs color flip";
            return;
            }
                                 // less than this one
         if(insVal < treeArray[curIn].getHeight() )
            curIn = 2*curIn+1;    // go to left child
         else                     // greater than this
            curIn = 2*curIn+2;    // go to right child
         if(curIn > ASIZE-1)
            {
            note = "CAN'T INSERT: Level is too deep";
            return;
            }
         }  // end while
      treeArray[curIn] = makePerson(insVal);
      if(curIn==0)             // if at root, make it black
         treeArray[curIn].setRed(false);
      oldArrow = curInOld;
      curInOld = curIn;
      drawAll = false;         // draw only this node
      drawMode = 1;
      check();                 // check r/b correcteness
      }  // end quickInsert()
//--------------------------------------------------------------
   public void quickRemove(boolean isNumb, int delVal)
      {
//      visitIndex = 0;
      curIn = 0;
      oldArrow = curInOld;
      curInOld = 0;      // arrow points to root
      if(!isNumb || delVal < 0 || delVal > MAX_KEY)
         {
         note = "Nodes have values from 0 to 99";
         return;      // inappropriate node number
         }
      while(delVal != treeArray[curIn].getHeight())
         {                      // value less than this node?
         if( delVal < treeArray[curIn].getHeight() )
            curIn = 2*curIn+1;  // go to left child
         else                   // value > this node
            curIn = 2*curIn+2;  // go to right child
                                // if too deep or null
         if(curIn > ASIZE-1 || treeArray[curIn] == null)
            {
            note = "Can't find node with that value";
            return;
            }
         }
      // found the node
      // if on bottom, or if no children, no complication
      if( curIn > 14 ||
          (treeArray[2*curIn+1]==null &&
           treeArray[2*curIn+2]==null) )
         {
         treeArray[curIn] = null;  // delete this node
         }
                                   // if no left child,
      else if(treeArray[2*curIn+1]==null)
         {                         // delete this node and
         treeArray[curIn] = null;  // plug in right subtree
         moveSubTree(2*(curIn+1), curIn);
         }
                                   // if no right child,
      else if(treeArray[2*curIn+2]==null)
         {                         // delete this node
         treeArray[curIn] = null;  // plug in left subtree
         moveSubTree(2*curIn+1, curIn);
         }
      else                         // node has two children
         {                         // get successor
         successor = inorderSuccessor(curIn);
         // put successor into this node
         treeArray[curIn] = treeArray[successor];
         // (note: successor cannot have a left child)
         int rightChild = 2*successor+2; // if successor has
                                         // right child
         if(successor<15 && treeArray[rightChild] != null)
            // move its right-child subtree into successor
            moveSubTree(2*(successor+1), successor);
         else  // successor does not have right child
            treeArray[successor] = null;  // delete successor
         }
      drawAll = true;                    // redraw all nodes
      check();                           // check r/b correctness
      }  // end quickRemove()
//--------------------------------------------------------------
   public int inorderSuccessor(int origNode)
      {
      // returns node with next-highest value after origNode
      // looks at rightChild, then rightChild's left descendents
      // (we can assume origNode has two children)
      int lastNode = origNode;
      int nextNode = 2*origNode+2;  // get right child
      while(nextNode < 31 && treeArray[nextNode] != null)
         {
         lastNode = nextNode;
         nextNode = 2*nextNode+1;   // left child, until bottom
         }
      return lastNode;
      }  // end inorderSuccessor()
//--------------------------------------------------------------
   // toggles colors of this node and two children,
   // provided children are the same, but different from this
   public void flip()
      {
      int lc = 2*curIn + 1;
      int rc = 2*(curIn+1);
      if(curIn > 14 || treeArray[lc]==null ||
                       treeArray[rc]==null )
         {
         note = "Node has no children";
         drawAll = false;
         drawMode = 0;
         return;
         }
                                    // if at root, and
      if(curIn == 0 &&              // children the same,
         treeArray[lc].getRed() == treeArray[rc].getRed() )
         {                          // flip children only
         treeArray[lc].setRed( !treeArray[lc].getRed() );
         treeArray[rc].setRed( !treeArray[rc].getRed() );
         drawAll = true;
         check();
         return;
         }
      // children not the same or parent not different
      if( treeArray[lc]==null || treeArray[rc]==null ||
          treeArray[lc].getRed() != treeArray[rc].getRed() ||
          treeArray[curIn].getRed() == treeArray[lc].getRed() )
         {
         note = "Can't flip this color arrangement.";
         drawAll = false;
         drawMode = 0;
         return;
         }
                                    // flip parent and children
      treeArray[curIn].setRed( !treeArray[curIn].getRed() );
      treeArray[lc].setRed( !treeArray[lc].getRed() );
      treeArray[rc].setRed( !treeArray[rc].getRed() );
      drawAll = true;
      check();
      }
//--------------------------------------------------------------
   public void rotateRight()
      {
      int y = curIn;    // top node, to be rotated around
      int leftChild;
      int rightChild;
      int rcrc;         // rightChild's rightChild
      int rclc;         // rightChild's leftChild
      int lclc;         // leftChild's leftChild
      int lcrc;         // leftChild's rightChild

      leftChild = 2*y + 1;
      if(treeArray[leftChild]==null)
         {
         note = "Can't rotate right; node has no left child";
         return;
         }

      // move y's rightChild subtree to
      //      y's rightChild's rightChild
      rightChild = 2*(y+1);
      rcrc = 2*(rightChild+1);
      moveSubTree(rightChild, rcrc);

      // move y to y's rightChild
      if(rightChild<31)
         treeArray[rightChild] = treeArray[y];

      // move y's leftChild to y
      treeArray[y] = treeArray[leftChild];
      if(leftChild>14)  // if child was on bottom row,
      treeArray[leftChild] = null;  // it's replaced by null

      // move y's leftChild's rightChild's subtree to
      // y's rightChild's leftChild
      lcrc = 2*(leftChild+1);
      rclc = 2*rightChild + 1;
      moveSubTree(lcrc, rclc);

      // move y's leftChild's leftChild's subtree to
      //      y's leftChild
      lclc = 2*leftChild + 1;
      moveSubTree(lclc, leftChild);
      drawMode = 2;                 // redraw all nodes
      check();                      // check r/b correctness
      }  // end rotateRight()
//--------------------------------------------------------------
   public void rotateLeft()
      {
      int y = curIn;    // y is node at top of rotation
      int leftChild;
      int rightChild;
      int rcrc;         // rightChild's rightChild
      int rclc;         // rightChild's leftChild
      int lclc;         // leftChild's leftChild
      int lcrc;         // leftChild's rightChild

      rightChild = 2*(y+1);
      if(treeArray[rightChild]==null)
         {
         note = "Can't rotate left, no right child";
         return;
         }
      // move y's leftChild subtree to
      //      y's leftChild's leftChild
      leftChild = 2*y + 1;
      lclc = 2*leftChild + 1;
      moveSubTree(leftChild, lclc);

      // move y to y's leftChild
      if(leftChild<31)
         treeArray[leftChild] = treeArray[y];

      // move y's rightChild to y
      treeArray[y] = treeArray[rightChild];
      if(rightChild>14)  // if child was on bottom row,
      treeArray[rightChild] = null;  // it's replaced by null

      // move y's rightChild's leftChild's subtree to
      // y's leftChild's rightChild
      rclc = 2*rightChild + 1;
      lcrc = 2*(leftChild+1);
      moveSubTree(rclc, lcrc);

      // move y's rightChild's rightChild's subtree to
      //      y's rightChild
      rcrc = 2*(rightChild+1);
      moveSubTree(rcrc, rightChild);
      drawMode = 2;                 // redraw all nodes
      check();                      // check r/b correctness
      }  // end rotateLeft
//--------------------------------------------------------------
   public void moveSubTree(int moveFrom, int moveTo)
      {
      int level;           // current level (top is 0)
      int rowPos;          // current horizontal position
      int index;           // current node index
      int rowLength;       // number of nodes in this row
      int topLevel;        // level of top of subtree
      int startRow;        // node index at left end of this row
      int tempTotal;       // persons in tempPerson array
      int tempCount;       // index of person being copied
      person[] tempPerson = new person[ASIZE];
                           // nodes must be on the screen
      if(moveFrom<0 || moveFrom>30)
         return;
      if(moveTo<0 || moveTo>30)
         return;
      // --------put moveFrom subtree in temporary array-------
      if(moveFrom==0)           // find level of top of subtree
         topLevel = 0;
      else if(moveFrom>0 && moveFrom<3)
         topLevel = 1;
      else if(moveFrom>2 && moveFrom <7)
         topLevel = 2;
      else if(moveFrom>6 && moveFrom <15)
         topLevel = 3;
      else
         topLevel = 4;
      startRow = moveFrom;
      index = startRow;           // index at start of row
      rowLength = 1;              // top of "pyramid"
      tempTotal = 0;
     // nested loops move each node of subtree in turn
     // index points to current node
                                  // outer loop: top-->bottom
      for(level=topLevel; level<5; level++)
         {                        // inner loop: left-->right
         for(rowPos=0; rowPos<rowLength; rowPos++)
            {                     // save node contents
            tempPerson[tempTotal++] = treeArray[index];
            treeArray[index] = null;  // it's gone from here
            index++;              // go right one node
            }  // end for(rowPos)
         startRow = 2*startRow+1; // start of next row down
         index = startRow;
         rowLength *= 2;          // twice as long as a level up
         }  // end for(level)

      // --------copy temporary array to moveTo-----------------
      if(moveTo==0)           // find level of top of subtree
         topLevel = 0;
      else if(moveTo>0 && moveTo<3)
         topLevel = 1;
      else if(moveTo>2 && moveTo <7)
         topLevel = 2;
      else if(moveTo>6 && moveTo <15)
         topLevel = 3;
      else
         topLevel = 4;
      startRow = moveTo;
      rowLength = 1;              // top of "pyramid"
      index = startRow;           // index at start of row
      tempCount = 0;
     // nested loops move each node of subtree in turn
     // index points to current node
                                  // outer loop: top-->bottom
      for(level=topLevel; level<5; level++)
         {                        // inner loop: left-->right
         for(rowPos=0; rowPos<rowLength; rowPos++)
            {                             // copy temp array
            if(tempCount < tempTotal)     // to new subtree
               treeArray[index] = tempPerson[tempCount++];
            else                          // node was moved
               treeArray[index] = null;   // up from level 5
            index++;              // go right one node
            }  // end for(rowPos)
         startRow = 2*startRow+1; // start of next row down
         index = startRow;
         rowLength *= 2;          // twice as long as a level up
         }  // end for(level)
      }  // end moveSubTree()
//--------------------------------------------------------------
   // transforms x, y mouse coordinates into index of node
   public int xyToIndex(int x, int y)
      {
      int column;                     // 0 to 31
      int level;                      // 0 to 4
      int index = 0;                  // 0 to 30
      column = ((x - leftMargin)*2) / horizSeparation;
      level =  (y - topMargin) / levelSeparation;
      switch(level)
         {
         case 0:                      // 0
            index = 0;
            break;
         case 1:                      // 1 or 2
            index = (column+9)/16;
            break;
         case 2:                      // 3 to 6
            index = (column+21)/8;
            break;
         case 3:                      // 7 to 14
            index = (column+27)/4;
            break;
         case 4:                      // 15 to 30
            index = (column+30)/2;
            break;
         }  // end switch
      return index;
      }  // end xyToIndex()
//--------------------------------------------------------------
   // gets mouseDown coords from RBTree, sets arrow (curInOld)
   public void setArrow(int index)
      {
      oldArrow = curInOld;
      curIn = curInOld = index;
      drawAll = false;
      drawMode = 0;
      }  // end setArrow()
//--------------------------------------------------------------
   // toggles red/black for specified node
   public void toggleRB()
      {
      if( treeArray[curInOld].getRed() == true )  // if red
         treeArray[curInOld].setRed(false);    // make it black
      else                                     // otherwise
         treeArray[curInOld].setRed(true);     // make it red
      note = "Toggled color at "+treeArray[curInOld].getHeight();
      drawAll = false;
      drawMode = 1;
      check();                      // check r/b correctness
      }
//--------------------------------------------------------------
   // check entire tree for RB correctness
   public void check()
      {
      // (root not counted in blackCount, since always black)
      int blackCount = -1;      // impossible count
      int oldBlackCount = -1;
      int pathsTaken = 0;       // counts paths followed so far
      int localCurIn = curIn;
      if(treeArray[0].getRed() == true)   // check root blackness
         {
         note = "ERROR: Root must be black";
         return;
         }
      // examine every cell, starting at most distant
      for(int j=30; j>0; j--)
         {
         if( treeArray[j] == null )       // if not occupied,
            continue;
                                          // or has two children,
         if( j<15 && (treeArray[2*j+1] != null &&
                      treeArray[2*j+2] != null ) )
            continue;                     // forget it

         // otherwise it's a leaf or it has one child
         oldArrow = curInOld;
         curInOld = curIn;
         drawAll = true;
         curIn = j;                       // start at leaf, or
                                          // one-child node
         blackCount = 0;                  // reset black count
         pathsTaken++;
         boolean lastRed = false;
         while(curIn > 0)                 // go back up, step by
            {                             // step, to level 1
            if(treeArray[curIn].getRed() == false) // it's black
               {
               blackCount++;             // count black nodes
               lastRed = false;
               }
            else                                   // it's red
               {
               if(lastRed==true)         // two reds in a row
                  {
                  note = "ERROR: parent and child are both red";
                  return;
                  }
               lastRed = true;
               }
            oldArrow = curInOld;
            curInOld = curIn;
            drawAll = true;
            curIn = (curIn-1)/2;          // go to parent
            }  // end while

         if(oldBlackCount == -1)          // first time
            oldBlackCount = blackCount;
         else if(blackCount != oldBlackCount)
            {
            note = "ERROR: Black counts differ";
            oldArrow = curInOld;
            curInOld = curIn = 0;
            drawAll = true;
            return;
            }
         else
            blackCount = 0;              // reset
         }  // end for(every cell)
                                         // if only one path,
         if(pathsTaken==1 && blackCount>0)  // and more blacks
            {                               // than root
            note = "ERROR: Black counts differ";
            oldArrow = curInOld;
            curInOld = curIn = 0;
            drawAll = true;
            return;
            }
      oldArrow = curInOld;   // return if tree is correct
      curInOld = curIn = localCurIn;   // restore pointer
      drawAll = true;
      note = "Tree is red-black correct";
      }  // end check()
//--------------------------------------------------------------
   }  // end class personGroup
////////////////////////////////////////////////////////////////
public class RBTree extends java.applet.Applet
                    implements Runnable, ActionListener,
                               MouseListener
   {
   private Thread runner;
   private int groupSize = 24;        // start with 24 items
   private personGroup thePersonGroup;
   private boolean runFlag;
   private int order = 1;             // 1=random, 2=backwards
   private int GPNumber = -1;         // general-purpose number
   private boolean isNumber = false;  // is GPNumber valid
   private TextField tf = new TextField("", 3);
   private int MAX_KEY = 99;
   private long lastWhen = 0;        // time of last mouse click
   private boolean itsSingleClick;
   private Button startButton, insButton, delButton,
                  flipButton, rolButton, rorButton, rbButton;
//--------------------------------------------------------------
   public void init()
      {
      addMouseListener(this);

      runFlag = false;
      thePersonGroup = new personGroup();
      setLayout( new FlowLayout() );
      Panel p1 = new Panel();
      add(p1);
      p1.setLayout( new FlowLayout() );

      Panel p2 = new Panel();
      p1.add(p2);
      p2.setLayout( new FlowLayout(FlowLayout.LEFT) );


      startButton = new Button("Start");  // Start button
      p2.add(startButton);
      startButton.addActionListener(this);

      insButton = new Button("Ins");      // Ins button
      p2.add(insButton);
      insButton.addActionListener(this);

      delButton = new Button("Del");      // Del button
      p2.add(delButton);
      delButton.addActionListener(this);

      flipButton = new Button("Flip");    // Flip button
      p2.add(flipButton);
      flipButton.addActionListener(this);

      rolButton = new Button("RoL");      // RoL button
      p2.add(rolButton);
      rolButton.addActionListener(this);

      rorButton = new Button("RoR");      // RoR button
      p2.add(rorButton);
      rorButton.addActionListener(this);

      rbButton = new Button("R/B");       // R/B button
      p2.add(rbButton);
      rbButton.addActionListener(this);

      Panel p3 = new Panel();
      p1.add(p3);
      p3.setLayout( new  FlowLayout(FlowLayout.RIGHT) );
      p3.add( new Label("Number: ") );
      p3.add(tf);
      thePersonGroup = new personGroup();  // start with tree
      thePersonGroup.fillRoot();           // with 1 person
      repaint();
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
      isNumber = true;
      String s = tf.getText();          // get the number
                                        // convert string
      try{ GPNumber = Integer.parseInt( s ); }  // to number
      catch(NumberFormatException e)
         {                              // not a number
         GPNumber = 0;
         isNumber = false;
         }
      // set draw() to use internal drawMode value
      thePersonGroup.setDrawAll(false);

      if(event.getSource() == startButton)     // "Start" button?
         thePersonGroup.fillRoot();
      else if(event.getSource() == insButton)  // "Ins" button?
         thePersonGroup.quickInsert(isNumber, GPNumber);
      else if(event.getSource() == delButton)  // "Del" button?
         thePersonGroup.quickRemove(isNumber, GPNumber);
      else if(event.getSource() == flipButton) // "Flip" button?
         thePersonGroup.flip();
      else if(event.getSource() == rolButton)  // "RoL" button?
         thePersonGroup.rotateLeft();
      else if(event.getSource() == rorButton)  // "RoR" button?
         thePersonGroup.rotateRight();
      else if(event.getSource() == rbButton)   // "R/B" button?
         thePersonGroup.toggleRB();
      repaint();                        // draw the tree
      try{ Thread.sleep(10); }
      catch(InterruptedException e)
          {  }
      }  // end action
//--------------------------------------------------------------
   public void run()
      {
      while(true)
         {  }
      }  // end run()
//--------------------------------------------------------------
   public void mousePressed(MouseEvent event)
      {
      int x = event.getX();
      int y = event.getY();
                                          // get node index
      int index = thePersonGroup.xyToIndex(x, y);

      if(event.getClickCount() == 1)      // single click
         {
         thePersonGroup.setArrow(index);
         repaint();
         }
      }  // end mouseDown()
//--------------------------------------------------------------
   public void mouseReleased(MouseEvent e)
      {  }
//--------------------------------------------------------------
   public void mouseEntered(MouseEvent e)
      {  }
//--------------------------------------------------------------
   public void mouseExited(MouseEvent e)
      {  }
//--------------------------------------------------------------
   public void mouseClicked(MouseEvent e)
      {  }
//--------------------------------------------------------------
   }  // end class Tree
////////////////////////////////////////////////////////////////


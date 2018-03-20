// Tree.java
// demonstrates binary tree
import java.awt.*;
import java.awt.event.*;
////////////////////////////////////////////////////////////////
class stack
   {
   private int[] st;
   private int top;
   public stack()            // constructor
      {
      st = new int[20];
      top = -1;
      }
   public void push(int j)   // put item on stack
      { st[++top] = j; }
   public int pop()          // take item off stack
      { return st[top--]; }
   public boolean isEmpty()  // true if nothing on stack
      { return (top == -1); }
   }
////////////////////////////////////////////////////////////////
class person
   {
   private int height;           // person height
   private Color color;          // person color

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
   private final int topMargin = 70;
   private final int leftMargin = 10;
   private final int textHeight = 13;
   private final int nodeDiameter = 20;
   private final int levelSeparation = 40;
   private final int horizSeparation = nodeDiameter + 6;
   private final int noteBoxTop = 45;
   private final int noteBoxHeight = 25;
   private final int noteBoxWidth = 200;
   private final int visitBoxTop = 280;
   private final int visitBoxHeight = 25;
   private final int visitBoxWidth = 430;
   private final int ASIZE = 31;  // maximum size of tree
   private final int MAX_KEY = 99;

   private person treeArray[];    // array for holding persons
   stack theStack = new stack();  // for traverse
   private int filledNodes;       // number of filled nodes
   private String note;           // displayed on screen
   private boolean isRand = true; // random or user-entered?
   private int value;             // value entered by user
   private int codePart = 1;      // which part of sequence?
   private int opMode;            // 1=Fill, 2=Find, 3=Ins, etc.
   private int curIn;             // current index
   private int curInOld;          // previous current index
   private int oldArrow;          // old arrow location
   private int visitArray[];      // holds 'visited' values
   private int visitIndex;        // index to visited values
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
      filledNodes = 0;
      note = "Press a button";
      visitArray = new int[ASIZE];   // array for 'visits'
      visitIndex = 0;
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
   public void setDrawAll(boolean mode)
      {                       // set by Tree, used by draw()
      drawAll = mode;         // true = draw all nodes
      }                       // false = use drawMode value
//--------------------------------------------------------------
   // calls doFill() to fill tree with random person objects
   public void fill(boolean isNumb, int fillVal)
      {
      if(opMode != 1)             // if we were in another mode,
         {
         opMode = 1;              // now we're in fill mode
         codePart = 1;            // take it from the top
         }
      switch(codePart)
         {
         case 1:
            visitIndex = 0;       // not traversing
            note = "Enter number of nodes (1 to 31)";
            curIn = 0;            // the usual reset
            oldArrow = curInOld;
            curInOld = 0;         // arrow points to root
            drawMode = 0;         // draw no nodes
            codePart = 2;
            break;
         case 2:
            if(!isNumb || fillVal < 0 || fillVal > 31)
               {
               note = "Inappropriate number of nodes";
               codePart = 1;      // inappropriate node number
               }
            else
               {
               note =
               "Will create tree of " + fillVal + " nodes";
               codePart = 3;
               }
            break;
         case 3:
            doFill(fillVal);      // fill the tree
            drawMode = 2;         // draw all nodes after fill
            note = "Press any button";
            oldArrow = curInOld;
            curInOld = 0;         // arrow points to root
            codePart = 1;
            break;
         }  // end switch
      }  // end fill()
//--------------------------------------------------------------
   public void doFill(int size)   // fill tree with 'size' nodes
      {
      int tooDeep = 0;            // number of attemps > level 4
      int value;                  // value of person height

      for(int j=0; j<ASIZE; j++)  // fill entire tree
         treeArray[j] = null;     // with null objects
      filledNodes = 0;
                                  // array to mark used keys
      boolean[] usedKeys = new boolean[MAX_KEY+1];
      for(int j=0; j<MAX_KEY+1; j++)  // mark them all unused
         usedKeys[j] = false;
                                  // until enough nodes
      while(filledNodes < size  && tooDeep < 100)
         {                        // to prevent duplicates,
         do {                     // wait for unused value
            value = (int)(java.lang.Math.random()*MAX_KEY);
            } while(usedKeys[value]==true);
         person temp = makePerson(value);  // make a person
         curIn = 0;               // start at root
         while(true)              // go from node to node
            {
            if(curIn > ASIZE-1)   // gone too deep?
               {
               ++tooDeep;         // count for safety
               break;
               }
            if(treeArray[curIn]==null)  // if current node empty
               {
               treeArray[curIn] = temp; // insert new person
               ++filledNodes;
               usedKeys[value] = true;  // mark value used
               break;
               }
            else                        // go to next node
               {                        // less than this one?
               if(value < treeArray[curIn].getHeight() )
                  curIn = 2*curIn+1;    // go to left child
               else                     // greater than this?
                  curIn = 2*curIn+2;    // go to right child
               }
            }  // end while(true)
         }  // end while(filledNodes)
      }  // end doFill()
//--------------------------------------------------------------
   public void find(boolean isNumb, int findVal)
      {
      if(opMode != 2)             // if we were in another mode,
         {
         opMode = 2;              // now we're in find mode
         codePart = 1;            // take it from the top
         }
      switch(codePart)
         {
         case 1:
            visitIndex = 0;       // not traversing
            note = "Enter key of node to find";
            curIn = 0;
            oldArrow = curInOld;
            curInOld = 0;         // arrow points to root
            drawMode = 0;         // draw no nodes
            codePart = 2;
            break;
         case 2:
            if(!isNumb || findVal < 0 || findVal > MAX_KEY)
               {
               note = "Nodes have values from 0 to 99";
               codePart = 1;      // inappropriate node number
               }
            else
               {
               note =
               "Will try to find node with key " + findVal;
               codePart = 3;
               }
            break;
         case 3:                  // is this the node?
            if( treeArray[curIn]==null )
               {
               note = "Can't find node with that value";
               codePart = 1;
               break;
               }
            if( findVal == treeArray[curIn].getHeight() )
               {
               note = "Have found node " + findVal;
               oldArrow = curInOld;
               curInOld = curIn;
               codePart = 4;
               break;
               }
            else                  // this is not the node,
               {                  // so look deeper
               oldArrow = curInOld;
               curInOld = curIn;  // value less than this node?
               if( findVal < treeArray[curIn].getHeight() )
                  {
                  curIn = 2*curIn+1;   // go to left child
                  note = "Going to left child";
                  }
               else               // value greater than this node
                  {
                  curIn = 2*curIn+2;   // go to right child
                  note = "Going to right child";
                  }
               codePart = 3;
               if(curIn > ASIZE-1)
                  {               // gone too deep
                  note = "Can't find node with that value";
                  codePart = 1;
                  }
               }  // end else (not the node)
            break;
         case 4:
            note = "Search is complete";
            codePart = 5;
            break;
         case 5:
            note = "Press any button";
            oldArrow = curInOld;
            curInOld = 0;
            codePart = 1;
            break;
         }  // end switch
      }  // end find()
//--------------------------------------------------------------
   // insert a node
   public void insert(boolean isNumb, int insVal)
      {
      if(opMode != 3)             // if we were in another mode,
         {
         opMode = 3;              // now we're in insert mode
         codePart = 1;            // take it from the top
         }
      switch(codePart)
         {
         case 1:
            visitIndex = 0;       // not traversing
            note = "Enter value of node to insert";
            curIn = 0;
            oldArrow = curInOld;
            curInOld = 0;         // arrow points to root
            drawMode = 0;         // draw no nodes
            codePart = 2;
            break;
         case 2:
            value = insVal;
            if(!isNumb || insVal < 0 || insVal > MAX_KEY)
               {
               note = "Nodes have values from 0 to 99";
               codePart = 1;      // inappropriate node number
               }
            else
               {
               note = "Will insert node with key " + value;
               codePart = 3;
               }
            break;
         case 3:
            oldArrow = curInOld;
            curInOld = curIn;     // remember index
            if(curIn > ASIZE-1)   // check for full tree
               {
               note = "Level is too great";
               codePart = 4;
               break;
               }
            if(treeArray[curIn]==null)  // if current node empty
               {                        // insert new person
               treeArray[curIn] = makePerson(value);
               value = treeArray[curIn].getHeight();
               note =
                   "Have inserted node with key " + value;
               ++filledNodes;
               curInOld = curIn;
               drawMode = 1;      // draw the inserted node
               codePart = 4;
               }
            else                  // not empty; go to next node
               {                  // less than this one
               if(value < treeArray[curIn].getHeight() )
                  {
                  curIn = 2*curIn+1; // go to left child
                  note = "Going to left child";
                  }
               else               // greater than this
                  {
                  curIn = 2*curIn+2; // go to right child
                  note = "Going to right child";
                  }
               codePart = 3;
               if(curIn > ASIZE-1)
                  {
                  note = "Can't insert: Level is too great";
                  codePart = 1;   // too deep
                  }
               drawMode = 0;      // draw no nodes
               }  // end else(go to next node)
            break;
         case 4:
            note = "Insertion completed";
            drawMode = 0;         // draw no nodes
            codePart = 5;
            break;
         case 5:
            note = "Press any button";
            oldArrow = curInOld;
            curInOld = 0;
            codePart = 1;
            break;
         }  // end switch
      }  // end insert()
//--------------------------------------------------------------
   public void remove(boolean isNumb, int delVal)
      {
      if(opMode != 4)             // if we were in another mode,
         {
         opMode = 4;              // now we're in insert mode
         codePart = 1;            // take it from the top
         }
      switch(codePart)
         {
         case 1:
               visitIndex = 0;    // not traversing
               note = "Enter key of node to delete";
               codePart = 2;
               curIn = 0;
               oldArrow = curInOld;
               curInOld = 0;      // arrow points to root
               drawMode = 0;      // draw no nodes
               break;
         case 2:
            if(!isNumb || delVal < 0 || delVal > MAX_KEY)
               {
               note = "Nodes have values from 0 to 99";
               codePart = 1;      // inappropriate node number
               }
            else
               {
               note =
               "Will try to delete node " + delVal;
               codePart = 3;
               }
            curIn = 0;                // start at root
            oldArrow = curInOld;
            curInOld = 0;
            break;
         case 3:                      // is this the node?
            if( treeArray[curIn]==null )
               {                      // end of the branch
               note = "Can't find node with that value";
               codePart = 1;
               break;
               }
            if( delVal == treeArray[curIn].getHeight() )
               {
               note = "Have found node to delete";
               oldArrow = curInOld;
               curInOld = curIn;
               codePart = 4;
               break;
               }
            else                      // this is not the node,
               {                      // so look deeper
               oldArrow = curInOld;
               curInOld = curIn;      // value < this node?
               if( delVal < treeArray[curIn].getHeight() )
                  {
                  curIn = 2*curIn+1;  // go to left child
                  note = "Going to left child";
                  }
               else                   // value > this node
                  {
                  curIn = 2*curIn+2;  // go to right child
                  note = "Going to right child";
                  }
               codePart = 3;
               if(curIn > ASIZE-1)
                  {                   // gone too deep
                  note = "Can't find node with that value";
                  codePart = 1;
                  }
               }  // end else (not the node)
            break;
         case 4:
            if( curIn > 14 ||         // if on bottom, or
                (treeArray[2*curIn+1]==null && // if no children,
                 treeArray[2*curIn+2]==null) )
               {
               note = "Will delete node without complication";
               codePart = 5;
               }
            else if(treeArray[2*curIn+1]==null)
               {                      // if no left child,
               note = "Will replace node with its right subtree";
               codePart = 6;
               }
            else if(treeArray[2*curIn+2]==null)
               {                      // if no right child,
               note = "Will replace node with its left subtree";
               codePart = 7;
               }
            else                      // two children
               {
               successor = inorderSuccessor(curIn);
               note = "Will replace node with " +
                      treeArray[successor].getHeight();
               codePart = 8;
               }
            break;
         case 5:
            treeArray[curIn] = null;  // delete this node
            note = "Node was deleted";
            drawMode = 2;             // draw all nodes
            codePart = 10;
            break;
         case 6:
            treeArray[curIn] = null;  // delete this node
            moveUpSubTree(1, curIn);  // plug in right subtree
            note = "Node was replaced by its right subtree";
            drawMode = 2;             // draw all nodes
            codePart = 10;
            break;
         case 7:
            treeArray[curIn] = null;  // delete this node
            moveUpSubTree(0, curIn);  // plug in left subtree
            note = "Node was replaced by its left subtree";
            drawMode = 2;             // draw all nodes
            codePart = 10;
            break;
         case 8:
            // put successor into this node
            // (successor was found in 'case 4' above)
               treeArray[curIn] = treeArray[successor];
            // note: successor cannot have a left child
            int rightChild = 2*successor+2; // if successor has
                                            // right child
            if(successor<15 && treeArray[rightChild] != null)
               {  // move subtree whose top is successor's
                  // right subtree
               int su = treeArray[successor].getHeight();
               note =
               "and replace "+su+" with its right subtree";
               drawMode = 0;
               codePart = 9;
               }
            else  // no children, so delete successor
               {
               treeArray[successor] = null;
               note = "Node was replaced by successor";
               drawMode = 2;
               codePart = 10;
               }
            break;
         case 9:
            // move right child subtree into successor
            moveUpSubTree(1, successor); // plug in
            note = "Removed node in 2-step process";
            drawMode = 2;                // draw all nodes
            codePart = 10;
            break;
         case 10:
            note = "Press any button";
            oldArrow = curInOld;
            curInOld = 0;
            codePart = 1;
            break;
         }  // end switch
      }  // end remove
//--------------------------------------------------------------
   public void moveUpSubTree(int hand, int moveTo)
      {
      // moveTo: deleted node to move subtree into
      // moveTo cannot have both left and right subtrees
      // hand: 0=move up left subtree, 1=move up right subtree
      if(moveTo>14 || moveTo<0)
         return;           // can't move into bottom row
      int subTop;          // top of subtree to be moved
      int curIn;           // roving index
      int rowLength;       // number of nodes in this row
      int topLevel;        // level of top of subtree
      int startRow;        // node index at left end of this row
      int posFromRight;    // position from right end of line
      int myParent;
      int moveToNode;      // node another node will move to

      if(hand==1)              // no left subtree
         subTop = 2*moveTo+2;  // subtree = right child of moveTo
      else                     // no right subtree
         subTop = 2*moveTo+1;  // subtree = left child of moveTo
                                      // (can't be level 0)
      if(subTop>0 && subTop<3)        // top of subtree = level 1
         topLevel = 1;
      else if(subTop>2 && subTop <7)  // top of subtree = level 2
         topLevel = 2;
      else if(subTop>6 && subTop <15) // top of subtree = level 3                          // level 3
         topLevel = 3;
      else                            // top of subtree = level 4
         topLevel = 4;
      startRow = subTop;          // new row at top
      curIn = startRow;           // index at start of row
      rowLength = 1;              // top of subree 'pyramid'

     // nested loops move each node of subtree in turn
     // curIn points to nodes in original positions
                                  // outer loop goes down levels
      for(int level=topLevel; level<5; level++)
         {                        // inner loop goes across nodes
         for(int rowPos=0; rowPos<rowLength; rowPos++)
            {                     // calculate destination node,
            myParent = (curIn-1)/2;   // which is up 1 and either
            posFromRight = rowLength-rowPos-1; // 1 left or right
            if(hand==1)           // no left subtree
               moveToNode = myParent - (posFromRight+1)/2;
            else                  // no right subtree
               moveToNode = myParent + (rowPos+1)/2;
                                  // move person to destination
            treeArray[moveToNode] = treeArray[curIn];
            if(level==4)          // if bottom row, nothing moves
                treeArray[curIn] = null;  // into this node
            curIn++;              // go right one node
            }  // end for(rowPos)
         startRow = 2*startRow+1; // start of next row down
         curIn = startRow;
         rowLength *= 2;          // twice as long as a level up
         }  // end for(level)
      }  // end moveUpSubTree()
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
   public void traverse()
      {
      if(opMode != 5)               // if we were in another mode,
         {
         opMode = 5;                // now we're in traverse mode
         codePart = 1;              // take it from the top
         }
      switch(codePart)
         {
         case 1:
            visitIndex = 0;         // new traverse
            note = "Will traverse tree in \"inorder\"";
            curIn = 0;             // start at root
            oldArrow = curInOld;
            curInOld = 0;          // arrow points to root
            drawMode = 0;          // draw no nodes
            codePart = 2;
            break;
         case 2:
            note = "Will check left child";
            codePart = 3;
            break;
         case 3:                  // node has left child?
            if(curIn>14 || treeArray[2*curIn+1]==null)
               {                  // add to 'visited' list
               note = "Will visit this node";
               codePart = 4;      // no
               }
            else
               {                  // yes
               theStack.push(curIn);  // save curIn
               curIn = 2*curIn+1;     // curIn <-- left child
               oldArrow = curInOld;
               curInOld = curIn;
               note = "Will check for left child";
               codePart = 3;      // look for left again
               }
            break;
         case 4:                  // visiting this node
            visitArray[visitIndex++] =
                                  treeArray[curIn].getHeight();
            note = "Will check for right child";
            codePart = 5;
            break;
         case 5:                  // node has right child?
            if(curIn>14 || treeArray[2*curIn+2]==null)
               {
               note = "Will go to root of last subtree";
               codePart = 6;      // no
               }
            else
               {                  // yes
               curIn = 2*curIn+2; // curIn <-- right child
               oldArrow = curInOld;
               curInOld = curIn;
               note = "Will check left child";
               codePart = 3;      // look for left again
               }
            break;
          case 6:
               if( theStack.isEmpty() )  // if stack empty,
                  {
                  note = "Done traversal";
                  codePart = 7;          // we're done
                  }
               else
                  {                      // pop a node
                  curIn = theStack.pop();
                  oldArrow = curInOld;
                  curInOld = curIn;      // add to visited list
                  note = "Will visit this node";
                  codePart = 4;   // go visit popped node
                  }
            break;
         case 7:
            note = "Press any button";
            oldArrow = curInOld;
            curInOld = 0;
            codePart = 1;
            break;
         }  // end switch
      }  // end traverse()
//--------------------------------------------------------------
   public void drawOneNode(Graphics g, int index)
      {
      if(treeArray[index]==null)
         return;
      int height = treeArray[index].getHeight();
      Color c = treeArray[index].getColor();
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
      g.setColor(c);                 // draw the circle
      g.fillOval(x, y, nodeDiameter, nodeDiameter);
      g.setColor(Color.black);
      g.drawOval(x, y, nodeDiameter, nodeDiameter);

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

      g.setColor(Color.lightGray);      // clear lower text area
      g.fillRect(leftMargin, visitBoxTop,
                 visitBoxWidth, visitBoxHeight );
      g.setColor(Color.black);          // in lower text area,
      String s = "";                    // draw nodes visited
      for(int j=0; j<visitIndex; j++)   // (for Trav)
         s += (visitArray[j]+" ");
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
   }  // end class personGroup
////////////////////////////////////////////////////////////////
public class Tree extends java.applet.Applet
                  implements Runnable, ActionListener
   {
   private Thread runner;
   private int groupSize = 24;           // start with 24 items
   private personGroup thePersonGroup;
   private boolean runFlag;
   private int order = 1;          // 1=random, 2=backwards
   private int GPNumber = -1;      // general-purpose number
   private boolean isNumber = false;  // is GPNumber valid
   private TextField tf = new TextField("", 3);
   private int MAX_KEY = 99;
   private Button fillButton, findButton, insButton,
                  travButton, delButton;
//--------------------------------------------------------------
   public void init()
      {
      runFlag = false;
      thePersonGroup = new personGroup();
      setLayout( new FlowLayout() );
      Panel p1 = new Panel();
      add(p1);
      p1.setLayout( new FlowLayout() );

      Panel p2 = new Panel();
      p1.add(p2);
      p2.setLayout( new FlowLayout(FlowLayout.LEFT) );

      fillButton = new Button("Fill");    // Fill button
      p2.add(fillButton);
      fillButton.addActionListener(this);

      findButton = new Button("Find");    // Find button
      p2.add(findButton);
      findButton.addActionListener(this);

      insButton = new Button("Ins");      // Ins button
      p2.add(insButton);
      insButton.addActionListener(this);

      travButton = new Button("Trav");    // Trav button
      p2.add(travButton);
      travButton.addActionListener(this);

      delButton = new Button("Del");      // Del button
      p2.add(delButton);
      delButton.addActionListener(this);
//    p2.add( new Button("Redo") );

      Panel p3 = new Panel();
      p1.add(p3);
      p3.setLayout( new  FlowLayout(FlowLayout.RIGHT) );
      p3.add( new Label("Enter number: ") );
      p3.add(tf);
      thePersonGroup = new personGroup();  // start with tree
      thePersonGroup.doFill(20);           // with 20 persons
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

      if(event.getSource() == fillButton)      // "Fill" button?
         thePersonGroup.fill(isNumber, GPNumber);
      else if(event.getSource() == findButton) // "Find" button?
         thePersonGroup.find(isNumber, GPNumber);
      else if(event.getSource() == insButton)  // "Ins" button?
         thePersonGroup.insert(isNumber, GPNumber);
      else if(event.getSource() == travButton) // "Trav" button?
         thePersonGroup.traverse();
      else if(event.getSource() == delButton)  // "Del" button?
         thePersonGroup.remove(isNumber, GPNumber);
//       else if( (String)arg == "Redo" )  // "Redo" button?
//          // set draw() to draw everything
//          thePersonGroup.setDrawAll(true);
      repaint();                        // all buttons
      try{ Thread.sleep(10); }
      catch(InterruptedException e)
          {  }
      }  // end actionPerformed
//--------------------------------------------------------------
   public void run()
      {
      while(true)
         {
         }
      }  // end run()
//--------------------------------------------------------------
   }  // end class Tree
////////////////////////////////////////////////////////////////


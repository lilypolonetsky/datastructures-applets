// Heap.java
// demonstrates heap
import java.awt.*;
import java.awt.event.*;
////////////////////////////////////////////////////////////////
class person
   {
   private int height;           // person height
   private Color color;          // person color

   public Color getColor()       // access color
      { return color; }

   public int getHeight()        // access height
      { return height; }

   public void setHeight(int h)
      { height = h; }

   public person(int h, Color c) // constructor
      {
      height = h;
      color = c;
      }
   }
/////////////////////////////////////////////////////////////////
// heap of person objects is stored in treeArray
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
   private final int noteBoxWidth = 250;
   private final int ASIZE = 31;  // maximum size of heap
   private final int MAX_KEY = 99;

   private person treeArray[];    // array for holding persons
   private int nNodes;            // number of filled nodes
   private String note;           // displayed on screen
   private int value;             // value entered by user
   private int codePart = 1;      // which part of sequence?
   private int opMode;            // 1=Fill, 2=Find, 3=Ins, etc.
   private int curIn;             // current index
   private int curInOld;          // previous current index
   private int oldArrow;          // old arrow location
   private boolean drawAll;       // draw all nodes or not
   private int drawMode = 3;      // draw: 0 = no nodes
                                  //    1 = 1 node (& ancestors)
                                  //    2 = 2 nodes (& ancestors)
                                  //    3 = all nodes
   private person tempNode;       // for trickle up, down
   private person blankNode;      // for "hole"
   private int largerChild;       // larger of two children
   private person largestNode;    // for remove()
   private int oldChild;          // for insert()
   private int oldHeight;         // for change()
//--------------------------------------------------------------
   public personGroup()              // constructor
      {
      treeArray = new person[ASIZE]; // array for tree
      for(int j=0; j<ASIZE; j++)
         treeArray[j] = null;        // fill with null objects
      nNodes = 0;
      note = "Press a button";
      blankNode = new person(-1, Color.lightGray);
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
   // calls doFill() to fill heap with random person objects
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
               "Will create heap of " + fillVal + " nodes";
               codePart = 3;
               }
            break;
         case 3:
            doFill(fillVal);      // fill the heap
            drawMode = 3;         // draw all nodes after fill
            note = "Press any button";
            oldArrow = curInOld;
            curInOld = 0;         // arrow points to root
            codePart = 1;
            break;
         }  // end switch
      }  // end fill()
//--------------------------------------------------------------
   public void doFill(int size)   // fill heap with 'size' nodes
      {
      int tooDeep = 0;            // number of attemps > level 4
      int value;                  // value of person height

      for(int j=0; j<ASIZE; j++)  // fill entire heap
         treeArray[j] = null;     // with null objects
      nNodes = 0;
                                  // array marks used key values
      boolean[] usedKeys = new boolean[MAX_KEY+1];
      for(int j=0; j<MAX_KEY+1; j++)  // mark them all unused
         usedKeys[j] = false;
                                  // until enough nodes
      while(nNodes < size  && tooDeep < 100)
         {                        // to prevent duplicates,
         do {                     // wait for unused value
            value = (int)(java.lang.Math.random()*MAX_KEY);
            } while(usedKeys[value]==true);
         usedKeys[value] = true;  // mark it used;
         person newNode = makePerson(value); // make a person
         treeArray[nNodes] = newNode;
         trickleUp(nNodes);
         nNodes++;
         }  // end while(nNodes)
      }  // end doFill()
// -------------------------------------------------------------
   public void trickleUp(int index)
      {
      // parent = (index-1)/2;
      tempNode = treeArray[index];    // save new node

      while( index > 0 &&               // if parent smaller,
             treeArray[(index-1)/2].getHeight() <
                         tempNode.getHeight() )
         {                              // move parent down
         treeArray[index] = treeArray[(index-1)/2];
         index = (index-1)/2;           // go up
         }  // end while
      treeArray[index] = tempNode;    // restore new node
      }  // end trickleUp()
// -------------------------------------------------------------
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
            curIn = 0;            // arrow points to root
            oldArrow = curInOld;
            curInOld = 0;
            if(nNodes > ASIZE-1)  // check for full heap
               {
               note = "Can't insert; no room in display";
               codePart = 10;
               }
            else
               {
               note = "Enter value of node to insert";
               codePart = 2;
               }
            drawMode = 0;            // draw no nodes
            break;
         case 2:
            value = insVal;
            if(!isNumb || insVal < 0 || insVal > MAX_KEY)
               {
               note = "Nodes have values from 0 to 99";
               codePart = 1;         // bad node number
               }
            else
               {
               note = "Will insert node with key " + value;
               codePart = 3;
               }
            drawMode = 0;         // draw no nodes
            break;
         case 3:                  // insert in first empty cell
            oldArrow = curInOld;
            curIn = curInOld = nNodes; // first empty cell
            treeArray[curIn] = makePerson(value);
            note = "Placed node in first empty cell";
            codePart = 4;
            drawMode = 1;
            break;
         case 4:                  // save bottom node
            tempNode = treeArray[curIn];  // save new node
            treeArray[curIn] = blankNode;   // blank its space
            note = "Saved new node; will trickle up";
            codePart = 5;
            drawMode = 1;
            break;
         case 5:                  // index <- parent
            // parent = (curIn-1)/2
            if( curIn > 0 && treeArray[(curIn-1)/2].getHeight() <
                                      tempNode.getHeight() )
               {                        // move full cell down
               treeArray[curIn] = treeArray[(curIn-1)/2];
               treeArray[(curIn-1)/2] = blankNode;  // blank old
               oldArrow = curInOld;
               oldChild = curIn;
               curInOld = curIn = (curIn-1)/2; // index <- parent
               note = "Moved empty node up";
               codePart = 5;
               drawMode = 2;  // (parent always drawn anyway)
               }
            else
               {
               note = "Trickle-up completed";
               codePart = 6;
               drawMode = 0;
               }
            break;
         case 6:                  // curIn <- bottom
            treeArray[curIn] = tempNode;
            note = "Inserted new node in empty node";
            codePart = 9;
            drawMode = 1;
            break;
         case 9:
            nNodes++;             // count the new node
            note = "Insert completed; node count is " + nNodes;
            drawMode = 0;         // draw no nodes
            codePart = 10;
            break;
         case 10:
            note = "Press any button";
            oldArrow = curInOld;
            curInOld = 0;
            codePart = 1;
            break;
         }  // end switch
      }  // end insert()
//--------------------------------------------------------------
   public void remove()
      {
      if(opMode != 4)             // if we were in another mode,
         {
         opMode = 4;              // now we're in insert mode
         codePart = 1;            // take it from the top
         }
      switch(codePart)
         {
         case 1:
            oldArrow = curInOld;
            curIn = curInOld = 0; // arrow points to root
            if(nNodes==0)
               {
               note = "Can't remove; heap empty";
               codePart = 1;
               }
            else                  // save the root (largest)
               {
               largestNode = treeArray[0];
               note = "Will remove largest node (" +
                      largestNode.getHeight() + ")";;
               codePart = 2;
               }
            drawMode = 0;         // draw no nodes
            break;
         case 2:                  // blank the root
            treeArray[0] = blankNode;
            note = "Will replace with \"last\" node (" +
                    treeArray[nNodes-1].getHeight() + ")";
            drawMode = 1;
            codePart = 3;
            break;
         case 3:                  // root <-- last node
            oldArrow = curInOld;
            curIn = curInOld = 0;
            treeArray[0] = treeArray[nNodes-1];
            treeArray[nNodes-1] = null;
            nNodes--;
            note = "Will trickle down";
            drawMode = 3;     // need to draw over deleted node
            codePart = 4;
            break;
         case 4:                  // save new root for trickle
            oldArrow = curInOld;
            curIn = curInOld = 0;
            tempNode = treeArray[0];
            treeArray[0] = blankNode;
            note = "Saved root node (" +
                   tempNode.getHeight() + ")";
            drawMode = 1;
            codePart = 5;
            break;
         case 5:                  // find larger child
            if(curIn <= (nNodes-1) / 2) // not on bottom row
               {
               int leftChild = 2*curIn+1;
               int rightChild = leftChild+1;
                                  // find larger child
               if(rightChild < nNodes &&  // rightChild exists?
                        treeArray[leftChild].getHeight() <
                        treeArray[rightChild].getHeight() )
                  largerChild = rightChild;
               else
                  largerChild = leftChild;

               if(treeArray[largerChild] != null) // exists?
                  {
                  note = "Key " + treeArray[largerChild].getHeight() +
                         " is larger child";
                  codePart = 6;
                  }
               else
                  {
                  note = "Node has no children, so done";
                  codePart = 7;
                  }
               }
            else  // on bottom row
               {
               note = "Reached bottom row; so done";
               codePart = 7;
               }
            drawMode = 0;
            break;
         case 6:                  // top >= largerChild?
            if( tempNode.getHeight() >=
                treeArray[largerChild].getHeight() )
               {
               note = "\"Last\" node larger; will insert it";
               drawMode = 0;
               codePart = 7;
               }
            else                  // top < largerChild
               {
               note = "Moved node up";          // shift child up
               treeArray[curIn] = treeArray[largerChild];
               treeArray[largerChild] = blankNode;
               oldArrow = curInOld;
               curIn = curInOld = largerChild;  // go down
               drawMode = 2;  // draw largerChild
               codePart = 5;
               }
            break;
         case 7:                  // curIn = top
            treeArray[curIn] = tempNode;
            note = "Inserted \"last\" node";
            drawMode = 1;
            codePart = 9;
            break;
         // no case 8
         case 9:
            note = "Finished deleting largest node (" +
                   largestNode.getHeight() + ")";
            drawMode = 0;             // draw all nodes
            codePart = 10;
            break;
         case 10:
            note = "Press any button";
            oldArrow = curInOld;
            curInOld = curIn = 0;
            codePart = 1;
            break;
         }  // end switch
      }  // end remove
//--------------------------------------------------------------
   public void change(boolean isNumb, int insVal)
      {
      if(opMode != 2)             // if we were in another mode,
         {
         opMode = 2;              // now we're in change mode
         codePart = 1;            // take it from the top
         }
      switch(codePart)
         {
         case 1:
            oldArrow = curInOld;
            curIn = curInOld = 0; // arrow points to root
            if(nNodes==0)
               {
               note = "Can't change; heap empty";
               codePart = 1;
               }
            else                  // save the root (largest)
               {
               note = "Click on node to be changed";
               codePart = 2;
               }
            drawMode = 0;         // draw no nodes
            break;
         case 2:
            note = "Type node's new key value";
            drawMode = 0;
            codePart = 3;
            break;
         case 3:
            value = insVal;
            if(!isNumb || insVal < 0 || insVal > MAX_KEY)
               {
               note = "Nodes have values from 0 to 99";
               codePart = 2;         // bad node number
               }
            else
               {
               oldHeight = treeArray[curIn].getHeight();
               note = "Will change node from " + oldHeight +
                      " to " + value;
               codePart = 4;
               }
            drawMode = 0;         // draw no nodes
            break;
         case 4:
            treeArray[curIn].setHeight(value);
            if(oldHeight < value)
               {
               note = "Key increased; will trickle up";
               codePart = 5;
               }
            else if(oldHeight > value)
               {
               note = "Key decreased; will trickle down";
               codePart = 8;
               }
            else
               {
               note = "Key not changed.";
               codePart = 16;
               }
            drawMode = 1;
            break;
         case 5:                  // trickle up
            tempNode = treeArray[curIn];  // save changed node
            treeArray[curIn] = blankNode;   // blank its space
            note = "Saved changed node (" +
                   tempNode.getHeight() + ")";
            codePart = 6;
            drawMode = 1;
            break;
         case 6:                  // index <- parent
            // parent = (curIn-1)/2
            if( curIn > 0 && treeArray[(curIn-1)/2].getHeight() <
                                      tempNode.getHeight() )
               {                        // move full cell down
               treeArray[curIn] = treeArray[(curIn-1)/2];
               treeArray[(curIn-1)/2] = blankNode;  // blank old
               oldArrow = curInOld;
               oldChild = curIn;
               curInOld = curIn = (curIn-1)/2; // index <- parent
               note = "Moved empty node up";
               codePart = 6;
               drawMode = 2;  // (parent always drawn anyway)
               }
            else
               {
               note = "Trickle-up completed";
               codePart = 7;
               drawMode = 0;
               }
            break;
         case 7:                  // curIn <- bottom
            treeArray[curIn] = tempNode;
            note = "Inserted changed item in empty node";
            codePart = 15;
            drawMode = 1;
            break;
         case 8:                  // trickle down
            tempNode = treeArray[curIn];  // save for trickle
            treeArray[curIn] = blankNode;
            note = "Saved changed node (" +
                   tempNode.getHeight() + ")";
            drawMode = 1;
            codePart = 9;
            break;
         case 9:                  // find larger child
            if(curIn <= (nNodes-1) / 2) // not on bottom row
               {
               int leftChild = 2*curIn+1;
               int rightChild = leftChild+1;
                                  // find larger child
               if(rightChild < nNodes &&  // rightChild exists?
                        treeArray[leftChild].getHeight() <
                        treeArray[rightChild].getHeight() )
                  largerChild = rightChild;
               else
                  largerChild = leftChild;

               if(treeArray[largerChild] != null) // exists?
                  {
                  note = "Key " +
                         treeArray[largerChild].getHeight() +
                         " is larger child";
                  codePart = 10;
                  }
               else
                  {
                  note = "Node has no children, so done";
                  codePart = 11;
                  }
               }
            else  // on bottom row
               {
               note = "Reached bottom row; so done";
               codePart = 11;
               }
            drawMode = 0;
            break;
         case 10:                  // top >= largerChild?
            if( tempNode.getHeight() >=
                treeArray[largerChild].getHeight() )
               {
               note = "Changed node is larger; will insert it";
               drawMode = 0;
               codePart = 11;
               }
            else                  // top < largerChild
               {
               note = "Moved empty node down";  // shift child up
               treeArray[curIn] = treeArray[largerChild];
               treeArray[largerChild] = blankNode;
               oldArrow = curInOld;
               curIn = curInOld = largerChild;  // go down
               drawMode = 2;  // draw largerChild
               codePart = 9;
               }
            break;
         case 11:                  // curIn = top
            treeArray[curIn] = tempNode;
            note = "Inserted changed node";
            drawMode = 1;
            codePart = 15;
            break;
         // no cases 12-14
         case 15:
            note = "Finished changing node (" +
                   treeArray[curIn].getHeight() + ")";
            drawMode = 0;
            codePart = 16;
            break;
         case 16:
            note = "Press any button";
            oldArrow = curInOld;
            curInOld = curIn = 0;
            codePart = 1;
            break;
         }  // end switch
      }  // end change()
//--------------------------------------------------------------
   // gets mouseDown coords, sets arrow (curInOld)
   public void setArrow(int index)
      {
      oldArrow = curInOld;
      curIn = curInOld = index;
      drawAll = false;
      drawMode = 0;
      }  // end setArrow()
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

      if(height >= 0)                // not (-1) blank node
         if(height < 10)             // draw height number
            g.drawString(""+height, x+7, y+nodeDiameter-5);
         else
            g.drawString(""+height, x+4, y+nodeDiameter-5);
      }  // end drawOneNode()
//--------------------------------------------------------------
   public void draw(Graphics g)      // draw the heap
      {
      int tempDrawMode, tempDex;
                                     // draw all nodes?
      tempDrawMode = (drawAll==true) ? 3 : drawMode;
      switch(tempDrawMode)
         {
         case 0:                     // draw no nodes
            break;
         case 2:                     // if rem or chng,
            if(opMode==4)
               drawOneNode(g, largerChild);  // draw largerChild
                                     // if ins or chng,

            if(opMode==3 || (opMode==2 && codePart==6) )
               drawOneNode(g, oldChild);     // draw child
            // intentionally no break
         case 1:                     // draw current & ancestors
            tempDex = curInOld;      // find parent
            while(tempDex > 0) // doesn't redraw root
               {
               drawOneNode(g, tempDex);  // draw node
               tempDex = (tempDex-1)/2;  // get node's parent
               }
            drawOneNode(g, 0);       // draw root
            break;
         case 3:                     // draw all nodes
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
public class Heap extends java.applet.Applet
                  implements Runnable, ActionListener,
                             MouseListener
   {
   private Thread runner;
   private personGroup thePersonGroup;
   private boolean runFlag;
   private int order = 1;          // 1=random, 2=backwards
   private int GPNumber = -1;      // general-purpose number
   private boolean isNumber = false;  // is GPNumber valid
   private TextField tf = new TextField("", 3);
   private int MAX_KEY = 99;
   private Button fillButton, chngButton, remButton, insButton;
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

      fillButton = new Button("Fill");   // Fill button
      p2.add(fillButton);
      fillButton.addActionListener(this);

      chngButton = new Button("Chng");   // Chng button
      p2.add(chngButton);
      chngButton.addActionListener(this);

      remButton = new Button("Rem");     // Rem button
      p2.add(remButton);
      remButton.addActionListener(this);

      insButton = new Button("Ins");     // Ins button
      p2.add(insButton);
      insButton.addActionListener(this);

      Panel p3 = new Panel();
      p1.add(p3);
      p3.setLayout( new  FlowLayout(FlowLayout.RIGHT) );
      p3.add( new Label("Enter number: ") );
      p3.add(tf);
      thePersonGroup = new personGroup();  // new heap
      thePersonGroup.doFill(10);           // with 10 items
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
      else if(event.getSource() == chngButton) // "Chng" button?
         thePersonGroup.change(isNumber, GPNumber);
      else if(event.getSource() == remButton)  // "Rem" button?
         thePersonGroup.remove();
      else if(event.getSource() == insButton)  // "Ins" button?
         thePersonGroup.insert(isNumber, GPNumber);
      repaint();                        // all buttons
      try{ Thread.sleep(10); }
      catch(InterruptedException e)
          {  }
      }  // end action
//--------------------------------------------------------------
   public void run()
      {
      while(true)
         {
         }
      }  // end run()
//--------------------------------------------------------------
   public void mousePressed(MouseEvent event)
      {
      int x = event.getX();
      int y = event.getY();
                                          // get node index
      int index = thePersonGroup.xyToIndex(x, y);

      if(event.getClickCount() == 1)
         {
         thePersonGroup.setArrow(index);
         repaint();
         }
      }  // end mousePressed()
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
   }  // end class Heap
////////////////////////////////////////////////////////////////


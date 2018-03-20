// GraphW.java
// demonstrates weighted graphs
import java.awt.*;
import java.awt.event.*;
////////////////////////////////////////////////////////////////
class priorityQ
   {
   // array in sorted order, from max at 0 to min at size-1
   private final int SIZE = 20;
   private edge[] queArray;
   private int size;

   public priorityQ()            // constructor
      {
      queArray = new edge[SIZE];
      size = 0;
      }

   public void insert(edge item)  // insert item in sorted order
      {
      int j;

      for(j=0; j<size; j++)           // find place to insert
         if( item.distance >= queArray[j].distance )
            break;

      for(int k=size-1; k>=j; k--)    // move items up
         queArray[k+1] = queArray[k];

      queArray[j] = item;             // insert item
      size++;
      }

   public edge removeMin()            // remove minimum item
      { return queArray[--size]; }

   public void removeN(int n)         // remove item at n
      {
      for(int j=n; j<size-1; j++)     // move items down
         queArray[j] = queArray[j+1];
      size--;
      }

   public edge peekMin()          // peek at minimum item
      { return queArray[size-1]; }

   public int size()              // return number of items
      { return size; }

   public boolean isEmpty()      // true if queue is empty
      { return (size==0); }

   public edge peekN(int n)      // peek at item n
      { return queArray[n]; }

   public int find(int findDex)  // find item with same index
      {
      for(int j=0; j<size; j++)
         if(queArray[j].destVert == findDex)
            return j;
      return -1;
      }
   }  // end class priorityQ
////////////////////////////////////////////////////////////////
class edge
   {
   public int srcVert;   // index of a vertex starting edge
   public int destVert;  // index of a vertex ending edge
   public int distance;  // distance from src to dest

   public edge(int sv, int dv, int d)  // constructor
      {
      srcVert = sv;
      destVert = dv;
      distance = d;
      }
   }
////////////////////////////////////////////////////////////////
class disIs                 // distance and isInTree flag
   {                        // items stored in adjacency matrix
   public int distance;
   public boolean isInTree; // true if edge is in tree
                            // (for display of heavier lines)
   disIs(int d, boolean i)
      {
      distance = d;
      isInTree = i;
      }
   }
///////////////////////////////////////////////////////////////
class vertex
   {
   public int x, y;                 // screen position
   public char label;               // label (e.g. 'A')
   public static char classChar;    // for sequence
   public Color color;              // color
   public boolean isInTree;
// ------------------
   public vertex(int xx, int yy)    // constructor
      {
      x = xx;                       // from mouse
      y = yy;
      label = classChar;            // A, B, C, etc.
      classChar++;
      int red = 100 + (int)(java.lang.Math.random()*154);
      int green = 100 + (int)(java.lang.Math.random()*154);
      int blue = 100 + (int)(java.lang.Math.random()*154);
      color = new Color(red, green, blue);
      isInTree = false;
      }
// ------------------
   }  // end class vertex
///////////////////////
class vertexGroup
   {
   private final int appletWidth = 440;
   private final int appletHeight = 300;
   private final int topMargin = 70;
   private final int leftMargin = 10;
   private final int textHeight = 13;
   private final int vertexDiameter = 22;
   private final int weightBoxWidth = 17;
   private final int weightBoxHeight = 15;
   private final int noteBoxTop = 45;
   private final int noteBoxHeight = 25;
   private final int noteBoxWidth = appletWidth-leftMargin;
   private final int visitBoxTop = 280;
   private final int visitBoxHeight = 25;
   private final int visitBoxWidth = appletWidth-leftMargin;
   private final int drawingBoxHeight = 207;
   private final int MAX_VERTS = 16;
   private final int MAX_WEIGHT = 99;
   private final int INFINITY = 1000000;

   private vertex vertexList[]; // list of vertices
   private disIs adjMat[][];    // adjacency matrix
   private disIs adjMat2[][];   // (for saving state)
   private int nVerts;          // current number of vertices
   private priorityQ thePQ;     // priority queue
   private int tree[];          // holds vertices in tree
   private int nTree;           // number of vertices in tree
   private String note;         // displayed on screen
   private String oldNote;      // for changeView()
   private int opMode;          // 1=mst, etc.
   private int codePart;        // section of code being executed
   private int drawMode;           // 1=draw msgs only
                                   // 2=msgs & vertex
                                   // 3=msgs, edge & 2 vertices
                                   // 4=everything
   private int xStartDrag, yStartDrag;
   private boolean madeVertex;  // false if made edge
   private boolean showAdjm;    // show adj matrix or graph?
   private int startingVertex;  // for searches
   private int currentVert;
   private int displayVertex;   // one vertex to display
   private int displayEdge1;    // vertex 1 of edge to display
   private int displayEdge2;    // vertex 2 of edge to displa
// ------------------
   public vertexGroup()         // constructor
      {
      vertex.classChar = 'A';
      vertexList = new vertex[MAX_VERTS]; // adjacency matrix
      adjMat = new disIs[MAX_VERTS][MAX_VERTS];
      adjMat2 = new disIs[MAX_VERTS][MAX_VERTS];
      nVerts = 0;
      thePQ = new priorityQ();            // priority queue
      tree = new int[MAX_VERTS];
      nTree = 0;
      for(int j=0; j<MAX_VERTS; j++)      // init adj matrix
         for(int k=0; k<MAX_VERTS; k++)   // to "infinity"
            {
            adjMat[j][k] = new disIs(INFINITY, false);
            adjMat2[j][k] = new disIs(INFINITY, false);
            }
      showAdjm = false;
      startingVertex = -1;
      note = "Double-click mouse to make vertex";
      drawMode = 4;
      }  // end constructor
// ------------------                  // called on double-click
   public void makeVertex(int x, int y)
      {
      madeVertex = true;
      if(nVerts > MAX_VERTS-1)
         {
         note = "CAN'T INSERT more vertices";
         return;
         }
      vertexList[nVerts++] = new vertex(x, y);
      note = "Made vertex " + vertexList[nVerts-1].label;
      displayVertex = nVerts-1;
      opMode = 0;
      drawMode = 2;
      }  // end makeVertex
// ------------------
   public void startDrag(int x, int y)  // called on mouseDown()
      {
      xStartDrag = x;
      yStartDrag = y;
      int v1 = closeTo(x, y);
      startingVertex = v1;
      if(v1 < 0)
         note = "To make edge, drag from vertex to vertex";
      else
         note = "Starting edge at vertex " +
                vertexList[v1].label;
      drawMode = 1;
      }  // end startDrag()
// ------------------
   public void endDrag(boolean isNumb, int value,
                       int x, int y)    // called on mouseUp()
      {
      if(madeVertex)  // not really a drag; just double-click
         {
         madeVertex = false;
         drawMode = 2;
         return;
         }
      int v1 = closeTo(xStartDrag, yStartDrag);
      int v2 = closeTo(x, y);
      if(opMode>0)
         {
         if(startingVertex == -1)
            note = "Click on a VERTEX";
         else
            note = "You clicked on "
                   + vertexList[startingVertex].label;
         drawMode = 1;
         }
      else if(v1<0 || v2<0 || v1==v2)        // bad drag
         {
         note = "CAN'T MAKE EDGE: Drag from vertex to vertex";
         drawMode = 1;
         }
      else if(isNumb != true || value<0 || value>MAX_WEIGHT)
         {
         note = "CAN'T MAKE EDGE: Enter a weight (0 to "
                + MAX_WEIGHT + ")";
         drawMode = 1;
         }
      else                                   // good drag
         {
         note = "Made edge from " + vertexList[v1].label +
                " to " + vertexList[v2].label +
                " with weight " + value;
         adjMat[v1][v2].distance = value;
         adjMat[v2][v1].distance = value;
         madeVertex = false;
         displayEdge1 = v1;
         displayEdge2 = v2;
         drawMode = 3;
         }
      }  // end endDrag()
// ------------------
   // returns  index in vertexList if (x, y) close to a vertex,
   // otherwise returns -1
   public int closeTo(int x, int y)
      {
      int r = vertexDiameter / 2;
      for(int j=0; j<nVerts; j++)
         {
         if( java.lang.Math.abs(vertexList[j].x - x) < r &&
             java.lang.Math.abs(vertexList[j].y - y) < r )
            return j;
         }
      return -1;
      }  // end closeTo()
// ------------------
   public void changeView()  // show adjacency matrix or graph?
      {                      // (called on View button press)
      if(showAdjm)
         {
         note = oldNote;     // recall previous instruction
         showAdjm = false;
         }
      else
         {
         oldNote = note;
         if(nVerts == 0)
            note = "No vertices; adjacency matrix is empty";
         else
            note = "Press View button again to show graph";
         showAdjm = true;
         drawMode = 4;
         }
      }  // end changeView()
// ------------------
   public void mst()      // minimum spanning tree
      {
      if(opMode != 1)
         {
         opMode = 1;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            saveState();
            note =
            "Single-click on vertex from which to start tree";
            startingVertex = -1;
            drawMode = 1;
            codePart = 2;
            break;
         case 2:
            // (assumes mouse click set startingVertex)
            if(startingVertex==-1)
               {
               note = "INVALID VERTEX";
               codePart = 1;
               }
            else
               {
               note = "Starting tree from vertex " +
                      vertexList[startingVertex].label;
               currentVert = startingVertex;
               codePart = 3;
               }
            drawMode = 1;
            break;
         case 3:
            tree[nTree++] = currentVert;  // insert cv in tree
            vertexList[currentVert].isInTree = true;
            note = "Placed vertex " +
                   vertexList[currentVert].label + " in tree";
            if(nTree == nVerts)  // are all verts in tree?
               codePart = 6;     // we're done
            else
               codePart = 4;     // not done
            drawMode = 4;        // to color the nodes in tree
            break;
         case 4:
            // insert verts adj to currentVert into PQ
            for(int j=0; j<nVerts; j++)  // for each vertex,
               {
               if(j==currentVert)        // skip if it's us
                  continue;
                                         // skip if in the tree
               if(vertexList[j].isInTree)
                  continue;

               int distance = adjMat[currentVert][j].distance;
               if(distance == INFINITY)  // skip if no edge
                  continue;
               putInPQ(j, distance);   // put it in PQ (maybe)
               }
            if(thePQ.size()>0)         // any vertices in PQ?
               {
               note = "Placed vertices adj to " +
                      vertexList[currentVert].label +
                      " in priority queue";
               codePart = 5;
               }
            else                       // PQ is empty, but
               {                       // vertices remain
               note = "Graph not connected";
               codePart = 8;
               }
            drawMode = 1;
            break;
         case 5:
            // remove edge with minimum distance from PQ
            edge theEdge = thePQ.removeMin();
            currentVert = theEdge.destVert;
            // mark the edge in the adj matrix
            int sourceVert = theEdge.srcVert;
            adjMat[sourceVert][currentVert].isInTree = true;
            adjMat[currentVert][sourceVert].isInTree = true;
            note = "Removed minimum-distance edge " +
                   vertexList[theEdge.srcVert].label +
                   vertexList[theEdge.destVert].label +
                   theEdge.distance +
                   " from priority queue";
            drawMode = 1;
            codePart = 3;
            break;
         case 6:
            note = "Press again to delete unmarked edges";
            drawMode = 1;
            codePart = 7;
            break;
         case 7:
            for(int j=0; j<nVerts; j++)      // unmark edges
               for(int k=0; k<nVerts; k++)
                  if(adjMat[j][k].distance != INFINITY)
                     // unmarked edges are removed
                     if( adjMat[j][k].isInTree == false)
                        adjMat[j][k].distance = INFINITY;
                     // marked changed to unmarked
                     else
                        adjMat[j][k].isInTree = false;
            note =
            "Minimum spanning tree; press again to restore tree";
            drawMode = 4;
            codePart = 8;
            break;
         case 8:
            restoreState();
            note = "Press any button";
            nTree = 0;                   // nothing in tree
            for(int j=0; j<nVerts; j++)        // clear marks
               vertexList[j].isInTree = false; //   from verts
            while( !thePQ.isEmpty() )    // clear PQ
               thePQ.removeMin();
            codePart = 1;
            opMode = 0;
            drawMode = 4;                // remove red circles
            break;
         }  // end switch
      }  // end mst
// ------------------
   public void saveState()
      {
      for(int j=0; j<nVerts; j++)
         for(int k=0; k<nVerts; k++)
            {
            adjMat2[j][k].distance = adjMat[j][k].distance;
            adjMat2[j][k].isInTree = adjMat[j][k].isInTree;
            }
      }
// ------------------
   public void restoreState()
      {
      for(int j=0; j<nVerts; j++)
         for(int k=0; k<nVerts; k++)
            {
            adjMat[j][k].distance = adjMat2[j][k].distance;
            adjMat[j][k].isInTree = adjMat2[j][k].isInTree;
            }
      }
// ------------------
   public void putInPQ(int newVert, int newDist)
      {
      // is there another edge with the same destination vertex?
      int queueIndex = thePQ.find(newVert);
      if(queueIndex != -1)
        {                              // yes
        edge tempEdge = thePQ.peekN(queueIndex);
        int oldDist = tempEdge.distance;
        if(oldDist > newDist)          // is new edge shorter?
           {                           // yes
           thePQ.removeN(queueIndex);  // remove old edge
           edge theEdge = new edge(currentVert, newVert, newDist);
           thePQ.insert(theEdge);      // insert new edge
           }
        // else no action; just leave the old vertex there
        }
     else                              // no edge with same d.v.
        {                              // so insert new one
        edge theEdge = new edge(currentVert, newVert, newDist);
        thePQ.insert(theEdge);
        }
      }  // end putInPQ()
// ------------------
   public String dtoS(int distance)
      {
      if(distance == INFINITY)
         return ("inf");
      else
         return ("" + distance);
      }
// ------------------
   public void warningNew()
      {
      note = "ARE YOU SURE? Press again to clear old graph";
      }
// ------------------
   public void drawOneVertex(Graphics g, int index)
      {
      if(index<0)
         return;
      Color c = vertexList[index].color;
      char ch = vertexList[index].label;
                                     // our coordinates
      int xBox = vertexList[index].x - vertexDiameter/2;
      int yBox = vertexList[index].y - vertexDiameter/2;

      g.setColor(c);                 // draw the circle
      g.fillOval(xBox, yBox, vertexDiameter, vertexDiameter);
      g.setColor(Color.black);
      g.drawOval(xBox, yBox, vertexDiameter, vertexDiameter);
                                     // red outline if in tree
      if(vertexList[index].isInTree)
         {
         g.setColor(Color.red);
         g.drawOval(xBox-3, yBox-3, vertexDiameter+6,
                                    vertexDiameter+6);
         }
                                     // draw label
      g.drawString(""+ch, xBox+8, yBox+vertexDiameter-5);
      }  // end drawOneVertex()
//--------------------------------------------------------------
   public void draw(Graphics g)      // draw the tree
      {
      int edgeDist;
      String s;
      if(showAdjm)
         {
         g.setColor(Color.yellow);   // clear applet screen
         g.fillRect(0, 0, appletWidth, appletHeight);

         g.setColor(Color.black);    // draw text ('note')
         g.drawString(note, leftMargin+6,
                      noteBoxTop+textHeight+6);
         drawAdjm(g);                // draw adjacency matrix
         return;
         }
      switch(drawMode)
         {
         // case 1: msgs only
         case 2:               // draw only one vertex
            drawOneVertex(g, displayVertex);
            break;
         case 3:               // draw one edge and two vertices
            edgeDist = adjMat[displayEdge1][displayEdge2].distance;
            if(edgeDist < INFINITY)
               drawEdge(g, displayEdge1, displayEdge2);
            drawOneVertex(g, displayEdge1);
            drawOneVertex(g, displayEdge2);
            break;
         case 4:              // draw all nodes and edges
            g.setColor(Color.lightGray); // clear applet screen
            g.fillRect(0, 0, appletWidth, appletHeight);
            g.setColor(Color.black);     // draw bounding rect
            g.drawRect(2, topMargin+1, appletWidth-4,
                                            drawingBoxHeight);
            for(int j=0; j<nVerts; j++)  // draw all edges
               for(int k=0; k<nVerts; k++)
                  {
                  edgeDist = adjMat[j][k].distance;
                  if(edgeDist < INFINITY)
                     drawEdge(g, j, k);
                  }
            for(int j=0; j<nVerts; j++)  // draw all vertices
               drawOneVertex(g, j);
            break;
         }  // end switch

     // display messages
     g.setColor(Color.lightGray);        // clear upper text area
     g.fillRect(leftMargin, noteBoxTop, noteBoxWidth,
                noteBoxHeight);
     g.setColor(Color.black);            // draw text ('note')
     g.drawString(note, leftMargin+6,
                  noteBoxTop+textHeight+6);

     g.setColor(Color.lightGray);        // clear lower text area
     g.fillRect(leftMargin, visitBoxTop,
                visitBoxWidth, visitBoxHeight);
     g.setColor(Color.black);

     if(opMode==1 )                      // min spanning tree
        {
        s = "Tree: ";                    // left side text area
        for(int j=0; j<nTree; j++)
           s += vertexList[ tree[j] ].label + " ";
        g.drawString(s, leftMargin, visitBoxTop+textHeight+3);

        s = "PQ: ";                      // right side text area
        for(int j=0; j<thePQ.size(); j++)
          {
          s += vertexList[ thePQ.peekN(j).srcVert ].label;
          s += vertexList[ thePQ.peekN(j).destVert ].label;
          s += thePQ.peekN(j).distance + " ";
      //    String temp = "" + thePQ.peekN(j).distance;
      //    s += temp.charAt(0) + " ";
          }
        g.drawString(s, leftMargin+200,
                             visitBoxTop+textHeight+3);
        }  // end if(opMode is 1)
      drawMode = 4;    // next time, draw everything
      }  // end draw()
//--------------------------------------------------------------
   private void drawEdge(Graphics g, int v1, int v2)
      {
      int x1 = vertexList[v1].x;
      int y1 = vertexList[v1].y;
      int x2 = vertexList[v2].x;
      int y2 = vertexList[v2].y;
      g.setColor(Color.black);
      g.drawLine(x1, y1, x2, y2);

      if(adjMat[v1][v2].isInTree)  // thick lines if
         {                         // edge is in tree
         g.drawLine(x1+1, y1, x2+1, y2);
         if( (x2-x1>0) != (y2-y1>0) )  // SW-->NE line
            g.drawLine(x1, y1-1, x2, y2-1);
         else                          // SE-->NW line
            g.drawLine(x1, y1+1, x2, y2+1);

         }
                                   // draw weight box
      int xHalfway = (x1+x2)/2 - weightBoxWidth/2;
      int yHalfway = (y1+y2)/2 - weightBoxHeight/2;
      g.setColor(Color.white);
      g.fillRect(xHalfway, yHalfway, weightBoxWidth,
                                             weightBoxHeight);
      g.setColor(Color.black);
      g.drawRect(xHalfway, yHalfway, weightBoxWidth,
                                             weightBoxHeight);
      int weight = adjMat[v1][v2].distance;
      int ff = (weight>9) ? 2 : 6;  // 1- or 2-digit spacing

      g.drawString( ""+weight, xHalfway+ff,
                                   yHalfway+weightBoxHeight-2);
      }  // end drawEdge()
//--------------------------------------------------------------
   public void drawAdjm(Graphics g)   // draw adjacency matrix
      {
      if(nVerts==0)
         {
         note = "No vertices; adjacency matrix is empty";
         return;
         }
      int leftMargin = 90;
      int topMargin = 106;
      int colWidth = 27;
      int rowHeight = 18;
                                              // horizontal rule
      g.drawLine(leftMargin-colWidth, topMargin-rowHeight+4,
                 leftMargin+nVerts*colWidth-colWidth+8,
                 topMargin-rowHeight+4);

      g.drawLine(leftMargin-colWidth/2+2,     // vertical rule
                 topMargin-2*rowHeight+8,
                 leftMargin-colWidth/2+2,
                 topMargin + (nVerts-1)*rowHeight);

      for(int row=0; row<nVerts; row++)       // row heads
         g.drawString(""+vertexList[row].label,
                      leftMargin - colWidth,
                      topMargin  + row*rowHeight);

      for(int col=0; col<nVerts; col++)       // column heads
         {
         g.drawString(""+vertexList[col].label,
                      leftMargin + col*colWidth,
                      topMargin  - rowHeight);

         for(int row=0; row<nVerts; row++)    // matrix data
            g.drawString(dtoS(adjMat[row][col].distance),
                         leftMargin + col*colWidth,
                         topMargin  + row*rowHeight);
         }
      }  // end drawAdjm
//--------------------------------------------------------------
   }  // end class vertexGroup
////////////////////////////
public class GraphW extends java.applet.Applet
                     implements Runnable, ActionListener,
                     MouseListener
   {
   private Thread runner;
   private vertexGroup theVertexGroup;
   private boolean wasClearPressed = false;
   private int GPNumber = -1;         // general-purpose number
   private boolean isNumber = false;  // is GPNumber valid?
   private TextField tf = new TextField("", 4);
   private Button newButton, treeButton, viewButton;
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

      newButton = new Button("New");       // New button
      p2.add(newButton);
      newButton.addActionListener(this);

      treeButton = new Button("Tree");     // Tree button
      p2.add(treeButton);
      treeButton.addActionListener(this);

      viewButton = new Button("View");     // View button
      p2.add(viewButton);
      viewButton.addActionListener(this);

      Panel p3 = new Panel();
      p1.add(p3);
      p3.setLayout( new FlowLayout(FlowLayout.RIGHT) );
      p3.add( new Label("Enter number: ") );
      p3.add(tf);

      theVertexGroup = new vertexGroup();
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
      { theVertexGroup.draw(gg); }
// ------------------
   public void update(Graphics gg)
      { paint(gg); }
// ------------------
   public void actionPerformed(ActionEvent event)
      {
      if(event.getSource() == newButton)       // "New" button?
         {
         if(wasClearPressed)                   // second press
            {
            wasClearPressed = false;
            theVertexGroup = new vertexGroup();
            }
         else                                  // first press
            {
            wasClearPressed = true;
            theVertexGroup.warningNew();
            }
         }
      else if(event.getSource() == treeButton) // "Tree" button?
         {
         theVertexGroup.mst();
         wasClearPressed = false;
         }
      else if(event.getSource() == viewButton) // "View" button?
         {
         theVertexGroup.changeView();
         wasClearPressed = false;
         }
      repaint();                       // all buttons
      try{ Thread.sleep(10); }
      catch(InterruptedException e)
          {  }
      }  // end actionPerformed()
// ------------------
   public void run()
      {
      while(true)
         {  }
      }  // end run()
// ------------------
   public void mousePressed(MouseEvent event)
      {
      int x = event.getX();
      int y = event.getY();
      wasClearPressed = false;
      if(event.getClickCount() == 1)       // single click
         theVertexGroup.startDrag(x, y);
      else if(event.getClickCount() == 2)  // double click
         theVertexGroup.makeVertex(x, y);
      repaint();
      }  // end mousePressed()
// ------------------
   public void mouseReleased(MouseEvent event)
      {
      int x = event.getX();
      int y = event.getY();
      String s = tf.getText();          // get the number
      isNumber = true;
      try{ GPNumber = Integer.parseInt( s ); }  // to number
      catch(NumberFormatException e)
         { isNumber = false; }          // not a number
      theVertexGroup.endDrag(isNumber, GPNumber, x, y);
      isNumber = false;                 // kill number in
      tf.setText("");                   // text field
      repaint();
      }  // end mouseReleased()
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
   }  // end class GraphW
//////////////////////////

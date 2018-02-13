// GraphN.java
// demonstrates non-directed graphs
import java.awt.*;
import java.awt.event.*;
////////////////////////////////////////////////////////////////
class stack
   {
   private final int SIZE = 20;
   private int[] st;
   private int top;
   public stack()            // constructor
      {
      st = new int[SIZE];
      top = -1;
      }
   public void push(int j)   // put item on stack
      { st[++top] = j; }
   public int pop()          // take item off stack
      { return st[top--]; }
   public int peek()         // peek at top of stack
      { return st[top]; }
   public boolean isEmpty()  // true if nothing on stack
      { return (top == -1); }
   public int size()         // return number of items on stack
      { return top+1; }
   public int peekN(int n)   // return value of item n
      { return st[n]; }
   }
////////////////////////////////////////////////////////////////
class Queue
   {
   private final int SIZE = 20;
   private int[] queArray;
   private int front;
   private int rear;

   public Queue()            // constructor
      {
      queArray = new int[SIZE];
      front = 0;
      rear = -1;
      }
   public void insert(int j) // put item at rear of queue
      {
      if(rear == SIZE-1)
         rear = -1;
      queArray[++rear] = j;
      }
   public int remove()       // take item from front of queue
      {
      int temp = queArray[front++];
      if(front == SIZE)
         front = 0;
      return temp;
      }
   public boolean isEmpty()  // true if queue is empty
      {
      return ( rear+1==front || (front+SIZE-1==rear) );
      }

   public int size()         // (assumes queue not empty)
      {
      if(rear >= front)             // contiguous sequence
         return rear-front+1;
      else                          // broken sequence
         return (SIZE-front) + (rear+1);
      }

   public int peekN(int n)   // (n==0 means n==front)
      {
      if(rear >= front)             // contiguous sequence
         return queArray[front+n];
      else                          // broken sequence
         if(n < SIZE-front)         // n on high end of array
            return queArray[front+n];
         else                       // n on low end of array
            return queArray[n-(SIZE-front)];
      }
   }  // end class Queue
////////////////////////////////////////////////////////////////
class vertex
   {
   public int x, y;                 // screen position
   public char label;               // label (e.g. 'A')
   public static char classChar;    // for sequence
   public Color color;              // color
   public boolean wasVisited;
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
      wasVisited = false;
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
   private final int noteBoxTop = 45;
   private final int noteBoxHeight = 25;
   private final int noteBoxWidth = 350;
   private final int visitBoxTop = 280;
   private final int visitBoxHeight = 25;
   private final int visitBoxWidth = 430;
   private final int drawingBoxHeight = 207;
   private final int MAX_VERTS = 20;

   private vertex vertexList[]; // list of vertices
   private int adjMat[][];      // adjacency matrix
   private int nVerts;          // current number of vertices
   private int adjMat2[][];     // (for saving state)
   private String note;         // displayed on screen
   private String oldNote;
   private int opMode;          // 1=DFS, 2=BFS, etc.
   private int codePart;        // section of code being executed
   private int drawMode;           // 1=draw msgs only
                                   // 2=msgs & vertex
                                   // 3=msgs, edge & 2 vertices
                                   // 4=everything
   private int xStartDrag, yStartDrag;
   private boolean madeVertex;  // false if made edge
   private boolean showAdjm;    // show adj matrix or graph?
   private int startingVertex;  // for searches
   private int currentVertex;
   private int displayVertex;   // one vertex to display
   private int displayEdge1;    // vertex 1 of edge to display
   private int displayEdge2;    // vertex 2 of edge to displa
   private stack theStack;
   private Queue theQueue;
   private char visitArray[];   // store labels of visited verts
   private int visitIndex;
// ------------------
   public vertexGroup()         // constructor
      {
      vertex.classChar = 'A';
      vertexList = new vertex[MAX_VERTS];
      adjMat = new int[MAX_VERTS][MAX_VERTS]; // adjacency matrix
      nVerts = 0;
      for(int j=0; j<MAX_VERTS; j++)      // set adjacency
         for(int k=0; k<MAX_VERTS; k++)   // matrix to 0
            adjMat[j][k] = 0;
      adjMat2 = new int[MAX_VERTS][MAX_VERTS];
      showAdjm = false;
      startingVertex = -1;
      theStack = new stack();
      theQueue = new Queue();
      visitArray = new char[MAX_VERTS];
      visitIndex = 0;
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
   public void endDrag(int x, int y)    // called on mouseUp()
      {
      if(madeVertex)  // not really a drag; just double-click
         {
         madeVertex = false;
         drawMode = 2;
         return;
         }
      int v1 = closeTo(xStartDrag, yStartDrag);
      int v2 = closeTo(x, y);
      if(opMode>0 && opMode<4 )              // dfs, bfs, tree
         {
         if(startingVertex == -1)
            note = "Click on a vertex";
         else
            note = "You clicked on "
                   + vertexList[startingVertex].label;
         drawMode = 1;
         }
      else if(v1<0 || v2<0 || v1==v2)        // bad drag
         {
         note = "CAN'T MAKE EDGE";
         drawMode = 1;
         }
      else                                   // good drag
         {
         note = "Made edge from " + vertexList[v1].label +
                " to " + vertexList[v2].label;
         adjMat[v1][v2] = 1;
         adjMat[v2][v1] = 1;
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
   public void dfs()  // depth-first search
      {
      if(opMode != 1)
         {
         opMode = 1;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            note =
            "Single-click on vertex from which to start search";
            startingVertex = -1;
            drawMode = 1;
            codePart = 2;
            break;
         case 2:
            // (assumes mouse click set startingVertex)
            if(startingVertex==-1)
               {
               note = "INVALID VERTEX";
               drawMode = 1;
               codePart = 1;
               }
            else
               {
               note = "Starting search from vertex " +
                      vertexList[startingVertex].label;
               while( !theStack.isEmpty() )   // clear stack
                  theStack.pop();
                                                  // begin
               vertexList[startingVertex].wasVisited = true;
               visitArray[visitIndex++] =
                               vertexList[startingVertex].label;
               theStack.push(startingVertex);
               codePart = 3;
               }
            displayVertex = startingVertex;
            drawMode = 2;
            break;
         case 3:
            if( !theStack.isEmpty() )
               {
               int v = getAdjUnvisitedVertex( theStack.peek() );
               if(v == -1)
                  {
                  theStack.pop();
                  if( !theStack.isEmpty() )
                     {
                     int temp = theStack.peek();
                     note = "Will check vertices adjacent to "
                                     + vertexList[temp].label;
                     }
                  else
                     note =
                     "No more vertices with unvisited neighbors";
                  drawMode = 1;
                  }
               else
                  {
                  note = "Visited vertex "
                                     + vertexList[v].label;
                  vertexList[v].wasVisited = true;
                  visitArray[visitIndex++] =
                                     vertexList[v].label;
                  theStack.push(v);
                  displayVertex = v;
                  drawMode = 2;
                  }
               codePart = 3;
               }  // end stack not empty
            else  // stack is empty, so search is done
               {
               note = "Press again to reset search";
               codePart = 4;
               drawMode = 1;
               }
            break;
         case 4:
            visitIndex = 0;                // reset visits
            for(int j=0; j<nVerts; j++)
               vertexList[j].wasVisited = false;
            note = "Press any button";
            codePart = 1;
            opMode = 0;
            drawMode = 4;
            break;
         }  // end switch
      }  // end dfs
// ------------------
                        // returns an unvisited vertex adj to v
   public int getAdjUnvisitedVertex(int v)
      {
      for(int j=0; j<nVerts; j++)
         if(adjMat[v][j]==1 && vertexList[j].wasVisited==false)
            return j;
      return -1;
      }  // end getAdjUnvisitedVert()
// ------------------
   public void bfs()   // breadth-first search
      {
      if(opMode != 2)
         {
         opMode = 2;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            note =
            "Single-click on vertex from which to start search";
            startingVertex = -1;
            drawMode = 1;
            codePart = 2;
            break;
         case 2:    // (assumes mouse click set startingVertex)
            if(startingVertex==-1)
               {
               note = "Invalid vertex";
               drawMode = 1;
               codePart = 1;
               }
            else
               {
               note = "Will start from vertex " +
                      vertexList[startingVertex].label;
               while( !theQueue.isEmpty() )   // clear queue
                  theQueue.remove();
                                                  // begin
               vertexList[startingVertex].wasVisited = true;
               visitArray[visitIndex++] =
                               vertexList[startingVertex].label;
               theQueue.insert(startingVertex);
               displayVertex = startingVertex;
               drawMode = 2;
               codePart = 3;
               }
            break;
         case 3:
            if( !theQueue.isEmpty() )
               {
               currentVertex = theQueue.remove();
               note = "Will check vertices adjacent to "
                  + vertexList[currentVertex].label;
               codePart = 4;
               }
            else  // queue is empty
               {
               note = "Press again to reset search";
               codePart = 5;
               }
            drawMode = 1;
            break;
         case 4:
            int v2 = getAdjUnvisitedVertex(currentVertex);
            if(v2 == -1)
               {
               note =
               "No more unvisited vertices adjacent to "
               + vertexList[currentVertex].label;
               drawMode = 1;
               codePart = 3;
               break;
               }
            else
               {
               note = "Visited vertex "
                                  + vertexList[v2].label;
               vertexList[v2].wasVisited = true;
               visitArray[visitIndex++] =
                                  vertexList[v2].label;
               theQueue.insert(v2);
               displayVertex = v2;
               drawMode = 2;
               }
            codePart = 4;
            break;
         case 5:
            visitIndex = 0;                // reset visits
            for(int j=0; j<nVerts; j++)
               vertexList[j].wasVisited = false;
            note = "Press any button";
            codePart = 1;
            opMode = 0;
            drawMode = 4;
            break;
         }  // end switch
      }  // end bfs()
// ------------------
   public void tree()  // dfs spanning tree
      {
      if(opMode != 3)
         {
         opMode = 3;
         codePart = 1;
         }
      switch(codePart)
         {
         case 1:
            saveState();
            note =
            "Single-click on vertex from which to start tree";
            startingVertex = -1;
            codePart = 2;
            drawMode = 1;
            break;
         case 2:
            // (assumes mouse click set startingVertex)
            if(startingVertex==-1)
               {
               note = "INVALID VERTEX";
               drawMode = 1;
               codePart = 1;
               }
            else
               {
               while( !theStack.isEmpty() )   // clear stack
                  theStack.pop();
                                                  // begin
               vertexList[startingVertex].wasVisited = true;
               visitArray[visitIndex++] =
                               vertexList[startingVertex].label;
               theStack.push(startingVertex);

               note = "Starting tree from vertex " +
                      vertexList[startingVertex].label;
               displayVertex = startingVertex;
               drawMode = 2;
               codePart = 3;
               }
            break;
         case 3:
            if( !theStack.isEmpty() )
               {
               currentVertex = theStack.peek();
               int v = getAdjUnvisitedVertex(currentVertex);
               if(v == -1)                  // no more nodes
                  {
                  theStack.pop();
                  if( !theStack.isEmpty() )
                     {
                     int temp = theStack.peek();
                     note = "Will check vertices adjacent to "
                                     + vertexList[temp].label;
                     }
                  else
                     {
                     note =
                     "No more vertices with unvisited neighbors";
                     }
                  drawMode = 1;
                  }
               else
                  {
                  note = "Visited vertex "
                                     + vertexList[v].label;
                  vertexList[v].wasVisited = true;
                  visitArray[visitIndex++] =
                                     vertexList[v].label;
                  theStack.push(v);

                  // mark edge from currentVertex to v
                  adjMat[currentVertex][v] = 2;
                  adjMat[v][currentVertex] = 2;
                  displayVertex = v;
                  displayEdge1 = currentVertex;
                  displayEdge2 = v;
                  drawMode = 3;
                  }
               codePart = 3;
               }  // end stack not empty
            else  // stack is empty
               {
               note = "Press again to delete unmarked edges";
               codePart = 4;
               }
            break;
         case 4:
            for(int j=0; j<nVerts; j++)      // unmark edges
               for(int k=0; k<nVerts; k++)
                  if(adjMat[j][k] == 1)      // unmarked
                     adjMat[j][k] = 0;       // are removed
                  else if(adjMat[j][k] == 2) // marked
                     adjMat[j][k] = 1;       // to unmarked
            note =
            "Minimum spanning tree; press again to restore tree";
            codePart = 5;
            break;
         case 5:
            restoreState();
            visitIndex = 0;                  // reset visits
            for(int j=0; j<nVerts; j++)
               vertexList[j].wasVisited = false;
            note = "Press any button";
            codePart = 1;
            opMode = 0;
            break;
         }  // end switch
      }  // end tree
// ------------------
   public void warningNew()
      {
      note = "ARE YOU SURE? Press again to clear old graph";
      }
// ------------------
   public void saveState()
      {
      for(int j=0; j<nVerts; j++)
         for(int k=0; k<nVerts; k++)
            adjMat2[j][k] = adjMat[j][k];
      }
// ------------------
   public void restoreState()
      {
      for(int j=0; j<nVerts; j++)
         for(int k=0; k<nVerts; k++)
            adjMat[j][k] = adjMat2[j][k];
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
                                     // red outline if "visited"
      if(vertexList[index].wasVisited)
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
      int edge;
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
            edge = adjMat[displayEdge1][displayEdge2];
            if(edge>0)
               drawEdge(g, displayEdge1, displayEdge2, edge);
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
                  edge = adjMat[j][k];
                  if(edge > 0)
                     drawEdge(g, j, k, edge);
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

     if(opMode>0 && opMode<4 )           // dfs=1, bfs=2, tree=3
        {
        String s = "Visits: ";
        for(int j=0; j<visitIndex; j++)
           s += visitArray[j] + " ";
        g.drawString(s, leftMargin+6, visitBoxTop+textHeight+3);

        if(opMode==1 || opMode==3)       // dfs or tree
           {
           s = "Stack (b-->t): ";
           for(int j=0; j<theStack.size(); j++)
             {
             int index = theStack.peekN(j);
             s += vertexList[index].label + " ";
             }
           }
        else                             // opMode==2; bfs
           {
           s = "Queue (f-->r): ";
           if( !theQueue.isEmpty() )
              for(int j=0; j<theQueue.size(); j++)
                 {
                 int index = theQueue.peekN(j);
                 s += vertexList[index].label + " ";
                 }
           }
        g.drawString(s, leftMargin+250,
                             visitBoxTop+textHeight+3);
        }  // end if(opMode is 1, 2, or 3)
      drawMode = 4;    // next time, draw everything
      }  // end draw()
//--------------------------------------------------------------
   private void drawEdge(Graphics g, int v1, int v2, int edge)
      {
      int x1 = vertexList[v1].x;
      int y1 = vertexList[v1].y;
      int x2 = vertexList[v2].x;
      int y2 = vertexList[v2].y;

      g.drawLine(x1, y1, x2, y2);  // thin line

      if(edge != 1)                // if edge is in tree (==2)
         {                         // make thick line
         g.drawLine(x1+1, y1, x2+1, y2);
         if( (x2-x1>0) != (y2-y1>0) )  // SW-->NE line
            g.drawLine(x1, y1-1, x2, y2-1);
         else                          // SE-->NW line
            g.drawLine(x1, y1+1, x2, y2+1);
         }
      }  // end drawEdge()
//--------------------------------------------------------------
   public void drawAdjm(Graphics g)   // draw adjacency matrix
      {
      if(nVerts==0)
         {
         note = "No vertices; adjacency matrix is empty";
         return;
         }
      int leftMargin = 95;
      int topMargin = 110;
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
            g.drawString(""+adjMat[row][col],
                         leftMargin + col*colWidth,
                         topMargin  + row*rowHeight);
         }
      }  // end drawAdjm
//--------------------------------------------------------------
   }  // end class vertexGroup
////////////////////////////
public class GraphN extends java.applet.Applet
                    implements Runnable, ActionListener,
                    MouseListener
   {
   private Thread runner;
   private vertexGroup theVertexGroup;
   private boolean wasClearPressed = false;
   private Button newButton, dfsButton, bfsButton,
                  treeButton, viewButton;
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

      dfsButton = new Button("DFS");       // DFS button
      p2.add(dfsButton);
      dfsButton.addActionListener(this);

      bfsButton = new Button("BFS");       // BFS button
      p2.add(bfsButton);
      bfsButton.addActionListener(this);

      treeButton = new Button("Tree");     // Tree button
      p2.add(treeButton);
      treeButton.addActionListener(this);

      viewButton = new Button("View");     // View button
      p2.add(viewButton);
      viewButton.addActionListener(this);

      theVertexGroup = new vertexGroup();
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
      { theVertexGroup.draw(gg); }
// ------------------
   public void update(Graphics gg)
      { paint(gg); }
// ------------------
   public void actionPerformed(ActionEvent event)
      {
      if(event.getSource() == newButton)       // "New" button?
         {
         if(wasClearPressed)           // second press?
            {
            wasClearPressed = false;
            theVertexGroup = new vertexGroup();
            }
         else                          // first press
            {
            wasClearPressed = true;
            theVertexGroup.warningNew();
            }
         }
      else if(event.getSource() == dfsButton)  // "DFS" button?
         {
         theVertexGroup.dfs();
         wasClearPressed = false;
         }
      else if(event.getSource() == bfsButton)  // "BFS" button?
         {
         theVertexGroup.bfs();
         wasClearPressed = false;
         }
      else if(event.getSource() == treeButton) // "Tree" button?
         {
         theVertexGroup.tree();
         wasClearPressed = false;
         }
      else if(event.getSource() == viewButton) // "View" button?
         {
         theVertexGroup.changeView();
         wasClearPressed = false;
         }
      repaint();                               // all buttons
      try{ Thread.sleep(10); }
      catch(InterruptedException e)
          {  }
      }  // end action
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
      theVertexGroup.endDrag(x, y);
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
   }  // end class GraphN
//////////////////////////


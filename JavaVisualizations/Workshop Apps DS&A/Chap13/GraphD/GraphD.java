// GraphD.java
// demonstrates directed, unweighted graph
import java.awt.*;
import java.awt.event.*;
////////////////////////////////////////////////////////////////
class vertex
   {
   public int x, y;                 // screen position
   public char label;               // label (e.g. 'A')
   public static char classChar;    // for sequence
   public Color color;              // color
   public boolean inTheTree;
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
      inTheTree = false;
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
   private final int dirDistance = 18;
   private final int dirSize = 7;
   private final int noteBoxTop = 45;
   private final int noteBoxHeight = 25;
   private final int noteBoxWidth = 350;
   private final int visitBoxTop = 280;
   private final int visitBoxHeight = 25;
   private final int visitBoxWidth = 430;
   private final int drawingBoxHeight = 207;
   private final int MAX_VERTS = 20;

   private vertex vertexList[]; // list of vertices
   private vertex vertexList2[]; // (for saving state)
   private int adjMat[][];      // adjacency matrix
   private int adjMat2[][];     // (for saving state)
   private int nVerts;          // current number of vertices
   private int nVerts2;         // (for saving state)
   private String note;         // displayed on screen
   private String oldNote;      // ( for changeView() )
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
   private char visitArray[];   // labels of in-the-tree verts
   private int visitIndex;
// ------------------
   public vertexGroup()         // constructor
      {
      vertex.classChar = 'A';
      vertexList = new vertex[MAX_VERTS];                                // adjacency matrix
      vertexList2 = new vertex[MAX_VERTS];                                // adjacency matrix
      adjMat = new int[MAX_VERTS][MAX_VERTS];
      adjMat2 = new int[MAX_VERTS][MAX_VERTS];
      nVerts = 0;
      for(int j=0; j<MAX_VERTS; j++)      // set adj matrix
         for(int k=0; k<MAX_VERTS; k++)   // to 0
            adjMat[j][k] = -1;
      showAdjm = false;
      startingVertex = -1;
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
         note = "Can't insert more vertices";
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
         note = "CAN'T MAKE EDGE: Drag from vertex to vertex";
         drawMode = 1;
         }
      else                                   // good drag
         {
         note = "Made edge from " + vertexList[v1].label +
                " to " + vertexList[v2].label;
         adjMat[v1][v2] = 1;
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
   public void topo()  // toplogical sort
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
            "Will perform topological sort";
            drawMode = 1;
            codePart = 2;
            break;
         case 2:
            if(nVerts > 0)
               {
               currentVertex = noSuccessors();
               if(currentVertex == -1)  // must be a cycle
                  {
                  note = "Cannot sort graph with cycles";
                  drawMode = 1;
                  codePart = 4;
                  }
               else  // currentVertex not -1
                  {
                  note = "Will remove vertex " +
                         vertexList[currentVertex].label;
                  drawMode = 1;
                  codePart = 3;
                  }
               }  // end nVerts>0
            else  // no more vertices; we're done
               {
               note = "Sort is complete; will restore graph";
               codePart = 4;
               }
            drawMode = 1;
            break;
         case 3:
            // insert vertices at _start_ of visitArray
            for(int j=visitIndex-1; j>=0; j--)   // move up
               visitArray[j+1] = visitArray[j];  // 1 space
            visitArray[0] = vertexList[currentVertex].label;
            visitIndex++;
            note = "Added vertex " +
                   vertexList[currentVertex].label +
                   " at start of sorted list";
            deleteVertex(currentVertex);
            drawMode = 4;
            codePart = 2;
            break;
         case 4:
            restoreState();
            note = "Will reset sort";
            drawMode = 4;
            codePart = 5;
            break;
         case 5:
            note = "Press any button";
            visitIndex = 0;
            codePart = 1;
            opMode = 0;
            drawMode = 1;
            break;
         }  // end switch
      }  // end dfs
// ------------------   // returns a vertex with no successors
   public int noSuccessors()
      {
      boolean isEdge;
      for(int row=0; row<nVerts; row++)
         {
         isEdge = false;
         for(int col=0; col<nVerts; col++)
            {
            if( adjMat[row][col] > 0 )
               {
               isEdge = true;
               break;
               }
            }
         if( !isEdge )
            return row;
         }
      return -1;                  // must be a cycle
      }  // end noSuccessors()
// ------------------
   public void deleteVertex(int delVert)
      {
      if(delVert == nVerts-1)      // if last vertex,
         {                         // no moving necessary
         nVerts--;
         return;
         }
                                   // delete from vertexList
      for(int j=delVert; j<nVerts-1; j++)
         vertexList[j] = vertexList[j+1];
                                   // delete row from adjMat
      for(int row=delVert; row<nVerts-1; row++)
         moveRowUp(row, nVerts);
                                   // delete col from adjMat
      for(int col=delVert; col<nVerts-1; col++)
         moveColLeft(col, nVerts-1);

      nVerts--;                             // one less vertex
      }
// ------------------
   private void moveRowUp(int row, int length)
      {
      for(int col=0; col<length; col++)
         adjMat[row][col] = adjMat[row+1][col];
      }
// ------------------
   private void moveColLeft(int col, int length)
      {
      for(int row=0; row<length; row++)
         adjMat[row][col] = adjMat[row][col+1];
      }
// ------------------
   public void saveState()
      {
      for(int j=0; j<nVerts; j++)
         vertexList2[j] = vertexList[j];
      for(int j=0; j<nVerts; j++)
         for(int k=0; k<nVerts; k++)
            adjMat2[j][k] = adjMat[j][k];
      nVerts2 = nVerts;
      }
// ------------------
   public void restoreState()
      {
      for(int j=0; j<nVerts2; j++)
         vertexList[j] = vertexList2[j];
      for(int j=0; j<nVerts2; j++)
         for(int k=0; k<nVerts2; k++)
            adjMat[j][k] = adjMat2[j][k];
      nVerts = nVerts2;
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
      if(vertexList[index].inTheTree)
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
            if(edge >= 0)
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
                  edge = adjMat[j][k];
                  if(edge >= 0)
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

     if(opMode>0 && opMode<4 )           // topo=1, bfs=2, tree=3
        {
        String s = "List: ";
        for(int j=0; j<visitIndex; j++)
           s += visitArray[j] + " ";
        g.drawString(s, leftMargin+6, visitBoxTop+textHeight+3);
        }  // end if(opMode is 1, 2, or 3)
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
      drawDirection(g, x1, y1, x2, y2);
      }  // end drawEdge()
//--------------------------------------------------------------
   // draws small circle, dirDistance from (x2, y2) end of edge
   public void drawDirection(Graphics g, int x1, int y1,
                                         int x2, int y2)
      {
      int adj = x1 - x2;
      int opp = y1 - y2;
      int hyp = (int)java.lang.Math.sqrt(adj*adj + opp*opp);
      int hypS = dirDistance;
      int adjS = (adj * hypS) / hyp;
      int oppS = (opp * hypS) / hyp;
      g.fillOval(x2+adjS-dirSize/2,
                 y2+oppS-dirSize/2, dirSize, dirSize);
      }
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
public class GraphD extends java.applet.Applet
                     implements Runnable, ActionListener,
                     MouseListener
   {
   private Thread runner;
   private vertexGroup theVertexGroup;
   private boolean wasClearPressed = false;
   private Button newButton, topoButton, viewButton;
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

      newButton = new Button("New");      // New button
      p2.add(newButton);
      newButton.addActionListener(this);

      topoButton = new Button("Topo");    // Topo button
      p2.add(topoButton);
      topoButton.addActionListener(this);

      viewButton = new Button("View");    // View button
      p2.add(viewButton);
      viewButton.addActionListener(this);

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
      if(event.getSource() == newButton)   // "New" button?
         {
         if(wasClearPressed)               // second press?
            {
            wasClearPressed = false;
            theVertexGroup = new vertexGroup();
            }
         else                              // first press
            {
            wasClearPressed = true;
            theVertexGroup.warningNew();
            }
         }
      if(event.getSource() == topoButton)  // "Topo" button?
         {
         theVertexGroup.topo();
         wasClearPressed = false;
         }
      if(event.getSource() == viewButton)  // "View" button?
         {
         theVertexGroup.changeView();
         wasClearPressed = false;
         }
      repaint();                       // all buttons
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
      if(event.getClickCount() == 1)             // single click
         theVertexGroup.startDrag(x, y);
      else if(event.getClickCount() == 2)        // double click
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
   public void mouseClicked(MouseEvent e)
      {  }
// ------------------
   public void mouseEntered(MouseEvent e)
      {  }
// ------------------
   public void mouseExited(MouseEvent e)
      {  }
// ------------------
   }  // end class Graph
//////////////////////////

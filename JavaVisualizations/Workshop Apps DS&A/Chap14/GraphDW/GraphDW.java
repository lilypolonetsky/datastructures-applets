// GraphDW.java
// demonstrates directed, weighted graphs
import java.awt.*;
import java.awt.event.*;
////////////////////////////////////////////////////////////////
class disP                // distance and parent
   {                      // items stored in sPath array
   public int parentVert; // current parent of this vertex
   public int distance;   // distance from start to this vertex

   public disP(int pv, int d)  // constructor
      {
      parentVert = pv;
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
   private final int appletHeight = 325;
   private final int topMargin = 70;
   private final int leftMargin = 10;
   private final int textHeight = 13;
   private final int vertexDiameter = 22;
   private final int dirDistance = 18;
   private final int dirSize = 7;
   private final int weightBoxWidth = 17;
   private final int weightBoxHeight = 15;
   private final int noteBoxTop = 45;
   private final int noteBoxHeight = 25;
   private final int noteBoxWidth = appletWidth-leftMargin;
   private final int visitBoxTop = 305;  // for table display
   private final int visitBoxHeight = 25;
   private final int visitBoxWidth = appletWidth-leftMargin;
   private final int charSpace = 40;     // for table display
   private final int headerBoxTop = 280;
   private final int drawingBoxHeight = 207;
   private final int MAX_VERTS = 13;
   private final int MAX_WEIGHT = 99;
   private final int INFINITY = 1000000;

   private vertex vertexList[]; // list of vertices
   private disIs adjMat[][];    // adjacency matrix
   private int nVerts;          // current number of vertices
   private int tree[];          // holds vertices in tree
   private int nTree;           // number of vertices in tree
   private String note;         // displayed on screen
   private String oldNote;      // for changeView()
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
   private int startTree;   // vertex clicked on, starts tree
   private int currentSrc;
   private int currentDest;
   private int startToCurrent;
   private int loopCounter;
   private int displayVertex;   // one vertex to display
   private int displayEdge1;    // vertex 1 of edge to display
   private int displayEdge2;    // vertex 2 of edge to displa
   private disP sPath[];        // array for shortest-path data
   private boolean willUpdate;  // sPath entry will be updated
   private int currentToFringe;      // distance from adj matrix
   private int startToFringe;  // distance from starting vertex
// ------------------
   public vertexGroup()         // constructor
      {
      vertex.classChar = 'A';
      vertexList = new vertex[MAX_VERTS]; // adjacency matrix
      sPath = new disP[MAX_VERTS];
      adjMat = new disIs[MAX_VERTS][MAX_VERTS];
      nVerts = 0;
      tree = new int[MAX_VERTS];
      nTree = 0;
      for(int j=0; j<MAX_VERTS; j++)      // set adj matrix
         for(int k=0; k<MAX_VERTS; k++)   // to "infinity"
            adjMat[j][k] = new disIs(INFINITY, false);
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
   public void path()   // shortest path
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
            "Single-click on starting vertex";
            startingVertex = -1;
            drawMode = 1;
            codePart = 2;
            break;
         case 2:
            // (assumes mouse click set startingVertex)
            if(startingVertex == -1)
               {
               note = "INVALID VERTEX";
               codePart = 1;
               }
            else
               {
               startTree = startingVertex;
               note = "Starting from vertex " +
                      vertexList[startTree].label;
               codePart = 3;
               }
            drawMode = 1;
            break;
         case 3:
            vertexList[startTree].isInTree = true;
            tree[0] = startTree;
            nTree = 1;
            note = "Added vertex " +
                   vertexList[startTree].label + " to tree";
            displayVertex = startTree;
            drawMode = 2;
            codePart = 4;
            break;
         case 4:
            // transfer row of distances from adjMat to sPath
            for(int j=0; j<nVerts; j++)
               {
               int tempDist = adjMat[startTree][j].distance;
               disP tempEdge = new disP(startTree, tempDist);
               sPath[j] = tempEdge;
               }
            note = "Copied row " +
               vertexList[startTree].label +
               " from adjacency matrix to shortest-path array";
            drawMode = 1;
            codePart = 5;
            break;
         case 5:               // find minimum distance in sPath
            int minDist = INFINITY;
            int indexMin = 0;
            for(int j=0; j<nVerts; j++)  // find minimum dist
               {
               if( !vertexList[j].isInTree )
                  {
                  int jDist = sPath[j].distance;
                  if(jDist < minDist)
                     {
                     minDist = jDist;
                     indexMin = j;
                     }
                  }
               }  // end for
            if(minDist == INFINITY)
               {
               note = "One or more vertices are UNREACHABLE";
               codePart = 12;
               }
            else
               {
               currentDest = indexMin;  // closest vertex
                                        // parent of closest v
               currentSrc = sPath[indexMin].parentVert;
                                        // distance between them
               startToCurrent = sPath[indexMin].distance;
               note = "Minimum distance from " +
                      vertexList[startTree].label + " is " +
                      startToCurrent + ", to vertex " +
                      vertexList[currentDest].label;
               codePart = 6;
               }
            drawMode = 1;
            break;
         case 6:              // put destination vertex in tree
            vertexList[currentDest].isInTree = true;
            tree[nTree++] = currentDest;
            note = "Added vertex " +
                   vertexList[currentDest].label + " to tree";
            adjMat[currentSrc][currentDest].isInTree = true;
            displayEdge1 = currentSrc;
            displayEdge2 = currentDest;
            if(nTree == nVerts)
               codePart = 12;
            else
               {
               loopCounter = 0;
               codePart = 7;
               }
            drawMode = 3;
            break;
         case 7:
            note = "Will adjust values in shortest-path array";
            drawMode = 1;
            codePart = 8;
            break;
         case 8:  // find next column holding non-tree vertex
            while( loopCounter < nVerts &&
                   vertexList[loopCounter].isInTree )
               loopCounter++;
            if(loopCounter == nVerts)
               {                   // if done,
               note =
                  "Finished all entries in shortest-path array";
               codePart = 5;       // go pick minimum
               break;
               }
            else
               {
               note = "Will compare distances for column " +
                      vertexList[loopCounter].label;
               codePart = 9;
               }
            drawMode = 1;
            break;
         case 9:  // calculate distance for one sPath entry
            // get distance from currentDest to loopCounter
            currentToFringe =
                    adjMat[currentDest][loopCounter].distance;
            // add distance from start to old currentVert
            startToFringe = startToCurrent + currentToFringe;
            // get distance of current sPath entry
            int sPathDist = sPath[loopCounter].distance;
            // compare distance from start with sPath entry
            String sign;
            if(startToFringe < sPathDist)
               {
               sign = " less than ";
               willUpdate = true;
               }
            else
               {
               sign = " greater than or equal to ";
               willUpdate = false;
               }
            // "A..D=2 + DB=in >= CB=3" or "A..D=2 + DB=4 < CB=7"
            note = "To " +
               vertexList[loopCounter].label + ":  " +

               vertexList[startTree].label + " to " +
               vertexList[currentDest].label + " (" +
               dtoS(startToCurrent) + ") plus edge " +

               vertexList[currentDest].label +
               vertexList[loopCounter].label + " (" +
               dtoS(currentToFringe) + ") " +

               sign + vertexList[startTree].label + " to " +
               vertexList[loopCounter].label + " (" +
               dtoS(sPathDist) + ")";
            codePart = 10;
            drawMode = 1;
            break;
         case 10:
            if(willUpdate)
               {                    // update sPath entry
               sPath[loopCounter].parentVert = currentDest;
               sPath[loopCounter].distance = startToFringe;
               note = "Updated array column " +
                      vertexList[loopCounter].label;
               }
            else
               {
               note = "No need to update array column " +
                      vertexList[loopCounter].label;
               }
            drawMode = 1;
            codePart = 11;
            break;
          case 11:
            if(++loopCounter < nVerts)
               {
               note = "Will examine next non-tree column";
               codePart = 8;   // not done all elements in sPath
               }
            else
               {
               note = "Done all entries in shortest-path array";
               codePart = 5;   // done with adjustment
               }               // go find minimum
            drawMode = 1;
            break;
         case 12:
            note = "All shortest paths from " +
            vertexList[startTree].label +
            " found; distances in array";
            codePart = 13;
            drawMode = 1;
            break;
         case 13:
            note = "Press again to reset paths";
            codePart = 14;
            drawMode = 1;
            break;
         case 14:
            nTree = 0;
            for(int j=0; j<nVerts; j++)
               {
               vertexList[j].isInTree = false;
               for(int k=0; k<nVerts; k++)
                  adjMat[j][k].isInTree = false;
               }
            note = "Press any button";
            codePart = 1;
            opMode = 0;
            drawMode = 4;
            break;
         }  // end switch
      }  // end path()
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

     if(opMode == 1 && codePart > 4)
        {
        for(int j=0; j<nVerts; j++)
           {                                 // draw sPath entry
           String tempStr = dtoS(sPath[j].distance); // distance
           s = tempStr + "(";
           int tempVert = sPath[j].parentVert;       // parent
           s +=vertexList[tempVert].label + ")";
           g.setColor(Color.black);
           g.drawString(s, leftMargin + charSpace*j,
                                 visitBoxTop+textHeight+3);
                                             // draw underline
           g.drawLine( leftMargin + charSpace*j,
                       headerBoxTop + textHeight+10,
                       leftMargin + charSpace*(j+1),
                       headerBoxTop + textHeight+10 );
           s = "" + vertexList[j].label;     // draw col heading
           if(vertexList[j].isInTree)
              g.setColor(Color.red);         // red if in tree
           else
              g.setColor(Color.black);
           g.drawString(s, leftMargin + charSpace*j,
                                 headerBoxTop+textHeight+3);
           }  // end for
        }  // end if(opMode)
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
      drawDirection(g, x1, y1, x2, y2);  // draw direction dot
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
public class GraphDW extends java.applet.Applet
                     implements Runnable, ActionListener,
                                          MouseListener
   {
   private Thread runner;
   private vertexGroup theVertexGroup;
   private boolean wasClearPressed = false;
   private int GPNumber = -1;         // general-purpose number
   private boolean isNumber = false;  // is GPNumber valid?
   private TextField tf = new TextField("", 4);
   private Button newButton, pathButton, viewButton;
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

      newButton = new Button("New");
      p2.add(newButton);
      newButton.addActionListener(this);

      pathButton = new Button("Path");
      p2.add(pathButton);
      pathButton.addActionListener(this);

      viewButton = new Button("View");
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
      if(event.getSource() == newButton) // "New" button?
         {
         if(wasClearPressed)             // second press?
            {
            wasClearPressed = false;
            theVertexGroup = new vertexGroup();
            }
         else                            // first press
            {
            wasClearPressed = true;
            theVertexGroup.warningNew();
            }
         }
      if(event.getSource() == pathButton) // "Path" button?
         {
         theVertexGroup.path();
         wasClearPressed = false;
         }
      if(event.getSource() == viewButton) // "View" button?
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
      if(event.getClickCount() == 1)         // single click
         theVertexGroup.startDrag(x, y);
      else if(event.getClickCount() == 2)    // double click
         theVertexGroup.makeVertex(x, y);
      repaint();
      }  // end mouseDown()
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
      { }
// ------------------
   public void mouseExited(MouseEvent e)
      { }
// ------------------
   public void mouseClicked(MouseEvent e)
      { }
// ------------------
   }  // end class Graph
//////////////////////////


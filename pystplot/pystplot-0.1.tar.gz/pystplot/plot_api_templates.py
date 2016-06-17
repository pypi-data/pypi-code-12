transforms_script_template = """/*
 * Created By Gustaf Sterner 2012-11-29
 */

/*
function getMaxOfArray(numArray) {
    return Math.max.apply(null, numArray);
}

function getMinOfArray(numArray) {
    return Math.min.apply(null, numArray);
}
*/

function Transform(min_x, max_x, min_y, max_y, canvasWidth, canvasHeight) {
    this.minX = min_x;
    this.maxX = max_x;
    this.minY = min_y;
    this.maxY = max_y;

    this.frameX = canvasWidth * 0.1;
    this.frameY = canvasHeight * 0.1;

    this.width = canvasWidth;
    this.height = canvasHeight;
}

Transform.translationToPlotCoordinate = function(plotLength, realLength, translation, frameStart) {
    return plotLength / realLength * translation + frameStart;
}

Transform.xToPlotCoordinate = function(width, xmax, xmin, xval, frameStart, frameEnd ) {
    return Transform.translationToPlotCoordinate(width - frameStart - frameEnd, xmax - xmin, xval - xmin, frameStart); 
}

Transform.yToPlotCoordinate = function(height, ymax, ymin, yval , frameStart, frameEnd ) {
    return Transform.translationToPlotCoordinate(height - frameStart - frameEnd, ymax - ymin, ymax - yval,  frameStart); 
}

Transform.prototype.xCoordinate = function(xval) {
    return Transform.xToPlotCoordinate(this.width, this.maxX, this.minX, xval, this.frameX, this.frameX);
}

Transform.prototype.yCoordinate = function(yval) {
    return Transform.yToPlotCoordinate(this.height, this.maxY, this.minY, yval, this.frameY, this.frameY);
}

Transform.prototype.xCoordinateArray = function(x_array) {
    var x_trans = [];
    for (i in x_array) {
        x_trans.push(this.xCoordinate(x_array[i]));
    }
    return x_trans;
}

Transform.prototype.yCoordinateArray = function(y_array) {
    var y_trans = [];
    for (i in y_array) {
        y_trans.push(this.yCoordinate(y_array[i]));
    }
    return y_trans;
}


/*******************************************/
function transformToPlotCoordinates(plotLength, realLength, translation, frameStart ) {
    return plotLength / realLength * translation + frameStart;
}


function transformX(width, xmax, xmin, xval, frameStart, frameEnd ) {
    return transformToPlotCoordinates (width - frameStart - frameEnd, xmax - xmin, xval - xmin, frameStart); 
}

function transformY(height, ymax, ymin, yval , frameStart, frameEnd ) {
    return transformToPlotCoordinates (height - frameStart - frameEnd, ymax - ymin, ymax - yval,  frameStart); 
}

function transformArrayToCoord(array, canvasWidth, transform, frameStart, frameEnd) {
    var vmin = Numerics.getMinOfArray(array);
    var vmax = Numerics.getMaxOfArray(array);
    var coordArray = [];
    for (i in array) {
        coordArray.push(transform(canvasWidth, vmax, vmin, array[i], frameStart, frameEnd));
    }
    return coordArray
}


function transformXArrayToCoord(xRealArray, canvasWidth) {
    var xmin = Numerics.getMinOfArray(xRealArray);
    var xmax = Numerics.getMaxOfArray(xRealArray);
    var xCoordArray = [];
    for (i in xRealArray) {
        xCoordArray.push(transformX(canvasWidth, xmax, xmin, xRealArray[i]));
    }
    return xCoordArray
}

function transformYArrayToCoord(yRealArray, canvasHeight) {
    var ymin = Numerics.getMinOfArray(yRealArray);
    var ymax = Numerics.getMaxOfArray(yRealArray);
    var yCoordArray = [];
    for (i in yRealArray) {
        yCoordArray.push(transformY(canvasHeight, ymax, ymin, yRealArray[i]));
    }
    return yCoordArray
}
"""

plotmain_script_template = """CSS_COLOR = {'red': '#FF0000', 
	     'green':'#00FF00', 
	     'blue':'#0000FF', 
	     'yellow':'#FFFF00',
	     'magenta':'#FF00FF',
	     'cyan':'#00FFFF',
	     'white':'#FFFFFF',
	     'black' : '#000000'};

function range(start, end, step)
{
    var returnArray = [];
    var tempSum = start;
    while(tempSum <= end) {
        returnArray.push(tempSum);
        tempSum += step;
    }    
    return returnArray;
}

function drawFrame(ctx, canvas_width, canvas_height, framex, framey) {
    ctx.strokeStyle = '#708090';
    ctx.strokeRect(framex,
	           framey,
                   canvas_width - 2 * framex,
		   canvas_height - 2 * framey) 	
}

function addExpression(ctx, expr, texty) {
    ctx.font="14px Arial";
    ctx.fillText(expr,10,texty);
}

function getDataAsArray(data_array, sub_index) {
    var return_array = [];
    for ( i = 0; i < data_array.length; i++) {
        return_array.push(data_array[i][sub_index]);
    }
    return return_array;
}

function getXData(data_array) {
    return getDataAsArray(data_array, 0);
}

function getYData(data_array) {
    return getDataAsArray(data_array, 1);
}

function drawPoint(ctx, x_value, y_value, stroke_style) {
      var radius = 4;
      ctx.beginPath();
      ctx.arc(x_value, y_value, radius, 0, 2 * Math.PI);
      ctx.fillStyle = stroke_style;
      ctx.closePath();
      ctx.fill();
}

function drawPoints(ctx, x_values, y_values, stroke_style) {
    for ( i = 0; i < x_values.length; i++) {
        drawPoint(ctx, x_values[i], y_values[i], stroke_style);
    }
}
function drawLine(ctx, x_values, y_values, stroke_style) {
    ctx.strokeStyle = stroke_style;
    ctx.lineWidth   = 2;
    ctx.beginPath();
    ctx.moveTo(x_values[0],y_values[0]);
    for ( i = 1; i < x_values.length; i++) {
        ctx.lineTo(x_values[i],y_values[i]);
    }
    ctx.stroke();
}

function drawSingleTicHorizontalAxis(ctx, trans, x_value, y_value) {
    var x_trans = trans.xCoordinate(x_value);
    var y_trans = trans.yCoordinate(y_value);
    ctx.strokeStyle = '#708090';
    ctx.beginPath();
    ctx.moveTo(x_trans, y_trans + 5);
    ctx.lineTo(x_trans,y_trans - 5);
    ctx.stroke();
    ctx.font="14px Arial";
    var text_shift_away = 10 + 14;
    var text_shift_center = 14;
    ctx.fillStyle = '#708090';
    ctx.fillText(x_value.toPrecision(4), x_trans - text_shift_center, y_trans + text_shift_away);
}

function drawGridLineHorizontalAxis(ctx, trans, x_value, y_min, y_max) {
    var x_trans = trans.xCoordinate(x_value);
    var y_min_trans = trans.yCoordinate(y_min);
    var y_max_trans = trans.yCoordinate(y_max);
    ctx.beginPath();
    ctx.moveTo(x_trans, y_min_trans);
    ctx.lineTo(x_trans, y_max_trans);
    ctx.stroke();
 }

function drawTicsHorizontalAxis(ctx, trans, tic_values, axis_value) {
    for ( i = 0; i < tic_values.length; i++) {
        drawSingleTicHorizontalAxis(ctx, trans, tic_values[i], axis_value);
    }    
}

function drawGridLinesHorizontalAxis(ctx, trans, tic_values, axis_value, axis_value_opposite) {
    ctx.strokeStyle = '#708090';
    ctx.setLineDash([2, 5]);
    for ( i = 1; i < tic_values.length - 1; i++) {
	drawGridLineHorizontalAxis(ctx, trans, tic_values[i], axis_value, axis_value_opposite)
    }    
    ctx.setLineDash([]);
}

function drawSingleTicVerticalAxis(ctx, trans, x_value, y_value) {
    var x_trans = trans.xCoordinate(x_value);
    var y_trans = trans.yCoordinate(y_value);
    ctx.strokeStyle = '#708090';
    ctx.beginPath();
    ctx.moveTo(x_trans + 5, y_trans);
    ctx.lineTo(x_trans - 5,y_trans);
    ctx.stroke();
    ctx.font="14px Arial";
    var text_shift_away = 20 + 7 * 4;
    var text_shift_center = 4;
    ctx.fillText(y_value.toPrecision(4), x_trans - text_shift_away, y_trans + text_shift_center);
}

function drawGridLineVerticalAxis(ctx, trans, x_min, x_max, y_value) {
    var x_min_trans = trans.xCoordinate(x_min);
    var x_max_trans = trans.xCoordinate(x_max);
    var y_trans = trans.yCoordinate(y_value);
    ctx.beginPath();
    ctx.moveTo(x_min_trans, y_trans);
    ctx.lineTo(x_max_trans, y_trans);
    ctx.stroke();
 }

function drawTicsVerticalAxis(ctx, trans, tic_values, axis_value) {
    for ( i = 0; i < tic_values.length; i++) {
        drawSingleTicVerticalAxis(ctx, trans, axis_value, tic_values[i]);
    }    
}

function drawGridLinesVerticalAxis(ctx, trans, tic_values, axis_value, axis_value_opposite) {
    ctx.strokeStyle = '#708090';
    ctx.setLineDash([2, 5]);
    for ( i = 1; i < tic_values.length - 1; i++) {
	drawGridLineVerticalAxis(ctx, trans, axis_value, axis_value_opposite, tic_values[i]);
    }    
   ctx.setLineDash([]);
}
 
function drawTics(ctx, trans, max_mins) {
    var x_tic_step = (max_mins.max_x - max_mins.min_x)/5;
    var x_tics_untransformed = range(max_mins.min_x, max_mins.max_x, x_tic_step);
    var y_tic_step = (max_mins.max_y - max_mins.min_y)/5;
    var y_tics_untransformed = range(max_mins.min_y, max_mins.max_y, y_tic_step);
    drawTicsHorizontalAxis(ctx, trans, x_tics_untransformed, max_mins.min_y);
    drawGridLinesHorizontalAxis(ctx, trans, x_tics_untransformed, max_mins.min_y, max_mins.max_y);
    drawTicsVerticalAxis(ctx, trans, y_tics_untransformed, max_mins.min_x);
    drawGridLinesVerticalAxis(ctx, trans, y_tics_untransformed, max_mins.min_x, max_mins.max_x);
}

function drawOnCanvas(canvas, trans, xArray, yArray, line_properties) {
//    var canvas=document.getElementById("subplot_4_4_0");
    var ctx=canvas.getContext("2d");
    var x_values = trans.xCoordinateArray(xArray);
    var y_values = trans.yCoordinateArray(yArray);

    if(line_properties.show_line) {
	drawLine(ctx, x_values, y_values, line_properties.stroke_style);
    }
    if(line_properties.show_points) {
	drawPoints(ctx, x_values, y_values, line_properties.stroke_style);
    }
}


function getLineDataX(plot_list, line_index) {
    var data_array = plot_list[line_index]["data"];
    return getXData(data_array);
}

function getLineDataY(plot_list, line_index) {
    var data_array = plot_list[line_index]["data"];
    return getYData(data_array);
}

function getLineStrokeStyle(plot_list, line_index) {
    if ('color' in plot_list[line_index]) {
	return CSS_COLOR[plot_list[line_index]['color']];
    }
    return CSS_COLOR['blue'];
}

function getShowLine(plot_list, line_index) {
    if ('lines' in plot_list[line_index]) {
	if( 'show' in plot_list[line_index]['lines'] ) {
	    return plot_list[line_index]['lines']['show'];
	}
    }
    return false;
}

function getShowPoints(plot_list, line_index) {
    if ('points' in plot_list[line_index]) {
	if( 'show' in plot_list[line_index]['points'] ) {
	    return plot_list[line_index]['points']['show'];
	}
    }
    return false;
}

function makeGlobalArrayX(plot_list) {
    globalArrayX = [];
    for ( line_index = 0; line_index < plot_list.length; line_index++) {
	globalArrayX = globalArrayX.concat(getLineDataX(plot_list, line_index));
    }
    return globalArrayX;
}

function makeGlobalArrayY(plot_list) {
    globalArrayY = [];
    for ( line_index = 0; line_index < plot_list.length; line_index++) {
	globalArrayY = globalArrayY.concat(getLineDataY(plot_list, line_index));
    }
    return globalArrayY;
}

function getGlobalMinMax(plot_list) {
    var min_x = Numerics.getMinOfArray(makeGlobalArrayX(plot_list));
    var max_x = Numerics.getMaxOfArray(makeGlobalArrayX(plot_list));
    var min_y = Numerics.getMinOfArray(makeGlobalArrayY(plot_list));
    var max_y = Numerics.getMaxOfArray(makeGlobalArrayY(plot_list));
    var max_mins = {
	'min_x' : min_x,
	'max_x' : max_x,
	'min_y' : min_y,
	'max_y' : max_y
    }
    return max_mins;
}

function getLineProperties(plot_list, line_index) {
    var stroke_style = getLineStrokeStyle(plot_list, line_index);
    var show_line = getShowLine(plot_list, line_index);
    var show_points = getShowPoints(plot_list, line_index);
    var line_properties = {
	'show_line' : show_line,
	'show_points' : show_points,
	'stroke_style' : stroke_style,
    }
    return line_properties;
}

function plotLineInList(canvas, plot_list, trans,  line_index) {
    // var data_array = plot_list[line_index]["data"];
    // var xArray = getXData(data_array);
    // var yArray = getYData(data_array);
    var xArray = getLineDataX(plot_list, line_index);
    var yArray = getLineDataY(plot_list, line_index);
    //Baka ihop nedan till en funktion
    //och skapa structen line_properties
    var stroke_style = getLineStrokeStyle(plot_list, line_index);
    var show_line = getShowLine(plot_list, line_index)
    var line_properties = getLineProperties(plot_list, line_index);
    drawOnCanvas(canvas, trans, xArray, yArray, line_properties);
}

function sternplotOnCanvas(canvas, plot_list) {
    var max_mins = getGlobalMinMax(plot_list);
    var canvas_width = canvas.width;
    var canvas_height = canvas.height;
    var frame_width = canvas.width * 0.1;
    var frame_height = canvas.height * 0.1;
    var trans = new Transform(max_mins.min_x, max_mins.max_x, max_mins.min_y, max_mins.max_y, canvas_width, canvas_height);
    for ( line_index = 0; line_index < plot_list.length; line_index++) {
        plotLineInList(canvas, plot_list, trans, line_index);
    }
    var ctx=canvas.getContext("2d");
    drawTics(ctx, trans, max_mins);
    drawFrame(ctx, canvas_width, canvas_height, frame_width, frame_height);
}

function sternplot(container, plot_list) {
    var canvas = document.createElement('canvas');
    canvas.width = container.offsetWidth;
    canvas.height = container.offsetHeight;
    container.appendChild(canvas);
    sternplotOnCanvas(canvas, plot_list)
    // for ( line_index = 0; line_index < plot_list.length; line_index++) {
    //     plotLineInList(canvas, plot_list, line_index);
    // }
    
    // var data_array = plot_list[0]["data"];
    // var xArray = getXData(data_array);
    // var yArray = getYData(data_array);
    // drawOnCanvas(container, xArray, yArray);
}
"""

numerics_script_template = """function Numerics(){}

Numerics.getMaxOfArray = function (numArray) { return Math.max.apply(null, numArray); }

Numerics.getMinOfArray = function (numArray) { return Math.min.apply(null, numArray); }

"""

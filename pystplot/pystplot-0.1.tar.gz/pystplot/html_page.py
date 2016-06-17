body_template="""
<html>
  <head>
    $plot_api_scripts
    <style type="text/css">
      body {
        margin: 0px;
        padding: 0px;
      }
    </style>
  </head>
  <body>
$plot_table
$function_call_tag
  </body>
</html>
"""
container_tag_template="""<div id="${container_id}" style="width : ${width}px; height : ${height}px; display: table-cell;"></div>"""

table_template="""
<div style="display: table;">
  ${table_row}
</div>"""

table_row_template="""<div style="display: table-row">
  ${container}
</div>"""


script_tag_template="""<script type="text/javascript">
$script
</script>"""

function_call_template = """      (function () {
        var
          container = document.getElementById('${container_id}'),
          plot_list = $plot_list_as_string,
          graph, i;

        // Draw Graph
        graph = sternplot(container, plot_list);

      })();"""

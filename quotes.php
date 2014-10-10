<html>
<head>
<link href="http://www.flotcharts.org/flot/examples/examples.css" rel="stylesheet" type="text/css">
<script language="javascript" tpye="text/javascript" src="../jquery-2.1.1.min.js"></script>
<script language="javascript" type="text/javascript" src="../flot/jquery.flot.js"></script>
</head>

<body>
<?php $tick = strtoupper($_GET["tick"]);
      $start = $_GET["begin"];
      $end = $_GET["end"];
      $step = $_GET["step"];
      $cmd = "python /usr/share/nginx/www/quotes/plots.py ".$tick." ".$start." ".$end." ".$step;
      exec($cmd); ?>
<img src="<?php echo $tick ?>.png" alt="DISPLAY ERROR" />
</body>
</html>

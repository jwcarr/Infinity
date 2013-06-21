<?php
/////////////////////////////////////////////////////////////////////////////////////////////////////////
// GLOBAL PARAMETERS
    
    // List of valid chain codes (default = [A, B, C, D])
    $chain_codes = array("A", "B", "C", "D");
    
    // Maximum generation number (default = 10)
    $max_generation_number = 10;
    
    // Magnitude of the stimuli sets (default = 50)
    $set_size = 50;
    
    // Amount of time for each training item in milliseconds (default = 5000)
    $time_per_training_item = 5000;
    
    // Delay before showing the training word in milliseconds (default = 1000)
    $word_delay = 1000;
    
    // Canvas width in pixels for the triangle stimuli (default = 500)
    $canvas_width = 500;
    
    // Canvas height in pixels for the triangle stimuli (default = 500)
    $canvas_height = 500;
    
    // Width of the unusable boarder area around the canvas in pixels (default = 10)
    $canvas_border = 10;
    
    // Thickness of the trianlge lines in pixels (default = 2)
    $triangle_line_thickness = 2;
    
    // Radius of the orienting spot in pixels (default = 8)
    $orienting_spot_radius = 8;
    
    // Minimum distance between points A and B on the triangle in pixels (default = 10)
    $min_distance_B = 10;
    
    // Minimum distance between point C and the line intersecting points A and B (default = 50)
    $min_distance_C = 50;

    // Set timezone for timestamps (default = UTC)
    date_default_timezone_set('UTC');
    
/////////////////////////////////////////////////////////////////////////////////////////////////////////
// GENERAL FUNCTIONS
    
    // Open a file
    function openFile($filename) {
        // If the file actually exists...
        if (file_exists($filename)) {
            // If the filesize > 0...
            if (filesize($filename) > 0) {
                // Open the file
                $file = fopen($filename, "r");
                // If you can secure a lock on the file...
                if (flock($file, LOCK_EX)) {
                    // Read the current data from the file...
                    $data = fread($file, filesize($filename));
                    // ... and then unlock it
                    flock($file, LOCK_UN);
                }
                // Close the file
                fclose($file);
                // Return the file's content
                return $data;
            }
            // If filesize is 0, return null
            return "";
        }
        // If the file does not exist, return False
        return False;
    }
    
    // Write data to a file
    function writeFile($filename, $data) {
        // If the file actually exists...
        if (file_exists($filename)) {
            // Open the file
            $file = fopen($filename, "w");
            // If you can secure a lock on the file...
            if (flock($file, LOCK_EX)) {
                // Write data to the file...
                fwrite($file, $data);
                // ... and then unlock it
                flock($file, LOCK_UN);
            }
            // Close the file
            fclose($file);
            // Return True to indicate success
            return True;
        }
        // If the file does not exist, return False        
        return False;
    }

    // Load the file for a given participant's dynamic or stable set
    function loadFile($condition, $chain_code, $generation, $set) {
        // Get the data from that file
        $data = openFile("data/". $condition ."/". $chain_code ."/". $generation . $set);
        // Read the file line by line
        $lines = explode("\n", $data);
        // Return the lines in an array
        return $lines;
    }

    // Get the words from a data file
    function getWords($condition, $chain_code, $generation, $set) {
        // Load in the file for a specific participant's dynamic set file
        $lines = loadFile($condition, $chain_code, $generation, $set);
        $n = count($lines);
        // Set up an empty array in which to dump the words
        $words = array();
        // For each line in the data file...
        for ($i=0; $i < $n; $i++) {
            // Separate out the columns delimited by tabs
            $columns = explode("\t", $lines[$i]);
            // If you're getting words from the stable set file...
            if ($set == "s") {
                // ... then remove the stimulus number information
                $remove_pipes = explode("|||", $columns[0]);
                // ... and the word is whatever comes after the triple pipe delimiter
                $word = $remove_pipes[1];
            }
            // If you're getting words from a dynamic set file...
            else {
                // ... then the word is just the first column
                $word = $columns[0];
            }
            // Dump the first column (the word) into the $words array
            array_push($words, $word);
        }
        // Return the words as an array
        return $words;
    }
    
    // Get a specific word from a given participant's dynamic set file
    function getWord($condition, $chain_code, $generation, $word_number) {
        // Get all words in that participant's dynamic file
        $words = getWords($condition, $chain_code, $generation, "d");
        // Return the requested word
        return $words[$word_number];
    }
    
    // Save the training score
    function saveTrainingScore($condition, $chain_code, $generation, $training_score) {
        // Open the scores file as it stands
        $data = openFile("data/scores");
        // Append the new data for this participant
        $new_data = $data ."\n". $condition. "\t". $chain_code ."\t". $generation ."\t". $training_score ."\t". date("d/m/Y H:i:s");
        // Write out the new file
        writeFile("data/scores", $new_data);
    }
    
    // Save a test answer to a participant's dynamic or stable set file
    function saveAnswer($condition, $chain_code, $generation, $position, $answer, $xy) {
        // Parse the map position into a set type ("d" or "s") and the stimulus number (0–49)
        $position = explode(".", $position);
        // If saving a dynamic file...
        if ($position[0] == "d") {
            // Concatenate the answer, XY coordinates, and timestamp (delimited by tabs)
            $answer = trim($answer) ."\t". $xy[0] .",". $xy[3] ."\t". $xy[1] .",". $xy[4] ."\t". $xy[2] .",". $xy[5] ."\t". date("H:i:s");
        }
        // If saving a stable file...
        else {
            // Concatenate the stimulus number, answer, XY coordinates, and timestamp (delimited by tabs)
            $answer = $position[1] ."|||". trim($answer) ."\t". $xy[0] .",". $xy[3] ."\t". $xy[1] .",". $xy[4] ."\t". $xy[2] .",". $xy[5] ."\t". date("H:i:s");
        }
        // Determine the filename you want to write to
        $filename = "data/". $condition ."/". $chain_code ."/". $generation . $position[0];
        // Read the content of that file as it currently stands
        $current_data = openFile($filename);
        // The new content of the file is the old data + the new answer
        $new_data = $current_data ."\n". $answer;
        // Write this new data to the file
       	writeFile($filename, trim($new_data));
    }
    
    // Save the final test item, and then sort the stable set into its unshuffled order
    function saveFinalAnswer($condition, $chain_code, $generation, $position, $answer, $xy) {
        // Import the global variable $set_size
        global $set_size;
        // Parse the map position into a set type ("d" or "s") and the stimulus number (0–49)
        $position = explode(".", $position);
        // Load in the lines from a specific stable set file
        $lines = loadFile($condition, $chain_code, $generation, "s");
        // Concatenate the stimulus number, answer, XY coordinates, and timestamp (delimited by tabs) for the final test item
        $answer = $position[1] ."|||". trim($answer) ."\t". $xy[0] .",". $xy[3] ."\t". $xy[1] .",". $xy[4] ."\t". $xy[2] .",". $xy[5] ."\t". date("H:i:s");
        // Add the final answer to the lines array
        array_push($lines, $answer);
        // Set up an empty array in which to dump the parsed lines
        $mappings = array();
        // For each line in the file...
        for ($i=0; $i < $set_size; $i++) {
            // Parse the line into its stimulus number and recorded data
            $parsed_line = explode("|||", $lines[$i]);
            // Put the recorded data into the $mappings array with a key equal to the stimulus number (also, append the order number (i) to the recorded data)
            $mappings[$parsed_line[0]] = $parsed_line[1] ."\t". ($i+1);
        }
        // Sorts the $mappings array by key
        ksort($mappings);
        // Implode the $mappings array, using a line break as the glue
        $new_data = implode("\n", $mappings);
        // Write the new data to the data file
        writeFile("data/". $condition ."/" . $chain_code ."/". $generation."s", $new_data);
    }
    
    // Clear the data files for a specific participant
    function clearFiles($condition, $chain_code, $generation) {
        // Overwrite the dynamic set file with "" (null)
        writeFile("data/". $condition ."/". $chain_code ."/". $generation."d", "");
        // Overwrite the stable set file with "" (null)
        writeFile("data/". $condition ."/". $chain_code ."/". $generation."s", "");
    }
    
/////////////////////////////////////////////////////////////////////////////////////////////////////////
// TRIANGLE STIMULI FUNCTIONS
    
    // Generate a random triangle stimulus
    function generateTriangle() {
        // Import global parameters
        global $canvas_width; global $canvas_height; global $canvas_border; global $min_distance_B; global $min_distance_C;
        
        // Choose coordinates for point A
        $x1 = rand($canvas_border+1, $canvas_width-$canvas_border);
        $y1 = rand($canvas_border+1, $canvas_height-$canvas_border);
        
        // Choose coordinates for point B
        $x2 = rand($canvas_border+1, $canvas_width-$canvas_border);
        $y2 = rand($canvas_border+1, $canvas_height-$canvas_border);
        
        // If and while point B is too close to point A, try a different set of coordinates for point B
        while (distance($x2, $y2, $x1, $y1) < $min_distance_B) {
            $x2 = rand($canvas_border+1, $canvas_width-$canvas_border);
            $y2 = rand($canvas_border+1, $canvas_height-$canvas_border);
        }
        
        // Determine the slope and intercept of the imaginary line that passes through points A and B
        if ($x1 == $x2) { $slope = 999999999; } else { $slope = ($y1 - $y2) / ($x1 - $x2); }
        $intercept = $y1 - ($slope * $x1);

        // Choose coordinates for point C
        $x3 = rand($canvas_border+1, $canvas_width-$canvas_border);
        $y3 = rand($canvas_border+1, $canvas_height-$canvas_border);
        
        // Given the X coordinate that you've chosen for point C, what point on the Y axis do you want to avoid to prevent skinnies?
        $y_avoid = $intercept + ($x3 * $slope);
        
        // If and while point C is too close to the avoid point, try a different Y coordinate for point C
        while (distance($x3, $y3, $x3, $y_avoid) < $min_distance_C) {
            $y3 = rand($canvas_border+1, $canvas_height-$canvas_border);
            
        }
        
        // Return an array containing the chosen X and Y coordinates
        return array($x1, $x2, $x3, $y1, $y2, $y3, $y_avoid);
    }
    
    // Load the coordinates for a particular triangle stimulus from a given data file
    function loadTriangle($condition, $chain_code, $generation, $stimulus_set, $stimulus_number) {
        // Load in the lines from a specific data file
        $lines = loadFile($condition, $chain_code, $generation, $stimulus_set);
        // Break those lines into columns using the tab as a delimiter
        $columns = explode("\t", $lines[$stimulus_number]);
        // Extract the XY coordinates for point A
        $xy1 = explode(",", $columns[1]);
        // Extract the XY coordinates for point B
        $xy2 = explode(",", $columns[2]);
        // Extract the XY coordinates for point C
        $xy3 = explode(",", $columns[3]);
        // Return the loaded coordinates
        return array($xy1[0], $xy2[0], $xy3[0], $xy1[1], $xy2[1], $xy3[1]);
    }
    
    // Measure the Euclidean distance between two points in 2D space
    function distance($xA, $yA, $xB, $yB) {
        // Yay Pythagoras!
        return sqrt(pow($xA - $xB, 2) + pow($yA - $yB, 2));
    }
    
/////////////////////////////////////////////////////////////////////////////////////////////////////////
// VALIDATION FUNCTIONS

    // Check that the chain code belongs to the global set of valid chain codes
    function checkChain($chain_code) {
        global $chain_codes;
        if (in_array($chain_code, $chain_codes) == True) { return True; } else { return False; }
    }

    // Check that the generation number does not exceed the global maximum generation number (and is greater than 0)
    function checkGen($generation_number) {
        global $max_generation_number;
        if ($generation_number > 0 AND $generation_number <= $max_generation_number) { return True; } else { return False; }
    }

    // Check that the output data files exist
    function checkDataFilesExist($condition, $chain_code, $generation) {
        $dynamic_file = file_exists("data/". $condition ."/" . $chain_code ."/" . $generation ."d");
        $stable_file = file_exists("data/". $condition ."/" . $chain_code ."/" . $generation ."s");
        if ($dynamic_file == True AND $stable_file == True) { return True; } else { return False; }
    }
    
    // Check that the input data files contain the correct number of lines (i.e. $set_size number of lines)
    function checkInputSet($condition, $chain_code, $generation) {
        global $set_size;
        $lines = loadFile($condition, $chain_code, ($generation-1), "d");
        if (count($lines) == $set_size) { return True; } else { return False; }
    }
    
    // Check that the required sound files are present and accounted for
    function checkSoundFiles($words) {
        // Set up an array to dump a list of missing sound files
        $missing_words = array();
        // For each word that needs a vocalization...
        for ($i = 0; $i < count($words); $i++) {
            // ... check that a sounds file exists
            if (file_exists("vocalizations/". $words[$i] .".m4a") == False) {
                // If not, add it to the missing words array
                $missing_words[] = $words[$i] . ".m4a";
            }
        }
        // Return the array of missing words
        return $missing_words;
    }
    
/////////////////////////////////////////////////////////////////////////////////////////////////////////
// DETERMINE CURRENT PAGE FROM "POST" OR "GET" DATA

    if ($_POST["page"] != "") { $page = $_POST["page"]; }
    elseif ($_GET["page"] != "") { $page = $_GET["page"]; }
    // Otherwise, goto the parameters page
    else { $page = "parameters"; }
    
/////////////////////////////////////////////////////////////////////////////////////////////////////////
// MAP READER AND MAP GENERATOR
//
// This bunch of code runs during the experiment. The MAP is generated prior to beginning the experiment,
// and describes the order in which everything is going to be presented. The MAP takes the form of:
//
//        BEGIN||TR-1||TR-2||TR-3|| ...etc... ||BREAK||TS-d.1||TS-s.2||TS-d.3|| ...etc... ||END
//
// BEGIN  =  Welcome page
// TR-i   =  Training page for training item i
// BREAK  =  Break page between training and test
// TS-a.i =  Test page for test item i in set a (a = either 'd' or 's')
// END    =  Experiment completed page
    
    if ($page == "experiment") {
        
        // Load in the variables from the previous page using either "get" or "post"
        if ($_GET["cond"] == "") {
            $cond = $_POST["cond"]; $chain = $_POST["chain"]; $gen = $_POST["gen"]; $map = $_POST["map"];
        }
        else {
            $cond = $_GET["cond"]; $chain = $_GET["chain"]; $gen = $_GET["gen"]; $map = $_GET["map"];
        }
        
        // Generate MAP if one hasn't been set up yet
        if ($map == "") {
            // First we want to present the welcome page
            $map = "BEGIN";
            
            // Shuffle the order in which the training items from the previous dynamic set will be presented
            $training_numbers = range(0, $set_size-1); shuffle($training_numbers);
            
            // Add the training pages to the map in this shuffled order
            for ($i=0; $i < $set_size; $i++) {
                $map = $map ."||TR-". $training_numbers[$i];
            }
            
            // Now add on the break page
            $map = $map ."||BREAK";
            
            // Shuffle the order in which the test items in both the dynamic and stable sets will be presented
            $dynamic_set = range(0, $set_size-1); shuffle($dynamic_set);
            $stable_set = range(0, $set_size-1); shuffle($stable_set);
            
            // Add the test pages to the map, interleaving the dynamic flow and stable flow
            for ($i=0; $i < $set_size; $i++) {
                $map = $map ."||TS-d.". $dynamic_set[$i] ."||TS-s.". $stable_set[$i];
            }

            // Finally we want to add on the experiment completed page
            $map = $map ."||END";
        }
        
        // Parse the map to determine what page to display now
        $map = explode("||", $map);
        
        // Parse the first map item for information about the stimulus number
        $map_position = explode("-", $map[0]);
        
        // Remove the first item from the map
        unset($map[0]);
        
        // Implode the map array back to a string using double pipe as the glue
        $new_map = implode("||", $map);
        
        // Set window location for next page for use in JavaScript below
        $window_location = "index.php?page=experiment&cond=". $cond ."&chain=". $chain ."&gen=". $gen ."&map=". $new_map;
        
        // If this page needs to be a training page, do the following...
        if ($map_position[0] == "TR") {
            // Get the training item from previous participants word set
            $training_word = getWord($cond, $chain, ($gen-1), $map_position[1]);
            // Update the current training score (i.e. how many training items the participant has correctly retyped.
            $score = $_GET["score"] + $_GET["correct"];
            // Modify the next window location with the current score
            $window_location = $window_location . "&score=" . $score;
        }
        
        // If this page needs to be a testing page, do the following...
        if ($map_position[0] == "TS") {
            // Parse the test item information into its set (either "d" or "s") and the stimulus number from that set (number between 0 and 49)
            $stimulus_info = explode(".", $map_position[1]);
            $stimulus_set = $stimulus_info[0];
            $stimulus_number = $stimulus_info[1];
        }
        
        // If this page needs to be a break page, do the following...
        if ($map_position[0] == "BREAK") {
            // Update the current training score (i.e. how many training items the participant has correctly retyped.
            $score = $_GET["score"] + $_GET["correct"];
            // Since training has now finished, save the score
            saveTrainingScore($cond, $chain, $gen, $score);
        }
    }

/////////////////////////////////////////////////////////////////////////////////////////////////////////
?>
<!DOCTYPE HTML>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Infinity</title>

<style type="text/css">
    .page {font-family: Helvetica Neue;}
    .head {color: #B22B3B; font-size: 30px}
    .body {color: black; font-size: 15px}
    .small {font-family: Helvetica Neue; color: black; font-size: 12px}
    .regular {font-family: Helvetica Neue; color: black; font-size: 16px}
    .large {font-family: Helvetica Neue; font-weight:lighter; color: black; font-size: 40px}
    .medium {font-family: Helvetica Neue; font-weight:lighter; color: black; font-size: 30px}
    .textfield {border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px;}
</style>

<?php if ($page == "experiment" AND $map_position[0] == "BREAK") { echo "<script src='countdown.js' type='text/javascript'></script>"; }?>

<script type="text/javascript">

// Location of the next page
var next_page_location = "<?php echo $window_location; ?>";

// Send to next page
function NextPage() { window.location = next_page_location; }

// Show the training item the play the vocalization
function ShowWord() { document.getElementById('alex').play(); document.f.a.value = '<?php echo $training_word; ?>'; }
        
// Hide the training item, then give focus to the response textbox
function HideWord() { document.f.a.value = ''; document.f.a.focus(); }
    
// Evaluate whether or not the participant correctly retyped the training item
function CheckWordMatch() { if (document.f.a.value == '') { return false; } else { if (document.f.a.value == '<?php echo $training_word; ?>') { document.getElementById('feedback').src = 'images/check.png'; setTimeout("NextItemCorrect()", 500); } else { document.getElementById('feedback').src = 'images/cross.png'; setTimeout("NextItemIncorrect()", 500); } return false; } }

// If training item was correctly retyped, send to next page and increase score by 1
function NextItemCorrect() { window.location = next_page_location + '&correct=1'; }

// If training item was not correctly retyped, send to next page and increase score by 0
function NextItemIncorrect() { window.location = next_page_location + '&correct=0'; }

// Applies to welcome page only. On pressing the 'enter key', move to the next page
function KeyCheck() { var keyID = event.keyCode; if (keyID == 13) { NextPage() } }

// When the training page loads, draw the triangle, set a delay for showing the training item, and set a delay for hiding the training item
function TrainingLoad() { DrawTriangle(); setTimeout("ShowWord()", <?php echo $word_delay; ?>); setTimeout("HideWord()", <?php echo $time_per_training_item; ?>); }

// When the testing page loads, draw the triangle, and then give focus to the response textbox
function TestingLoad() { DrawTriangle(); document.f.a.focus(); }  
        
<?php        
    // If we are currently on a training or test page...
    if ($map_position[0] == "TR" OR $map_position[0] == "TS") {
        // If we are currently on a training page...
        if ($map_position[0] == "TR") {
            // Get the XY coordinates for a given stimulus number from the previous participant's dynamic set file
            $xy = loadTriangle($cond, $chain, ($gen-1), "d", $map_position[1]);
        }
        // If we are currently on a test page...
        else {
            // If the current test item belongs to the dynamic flow...
            if ($stimulus_set == "d") {
                // Generate random XY coordinates
                $xy = generateTriangle();
            }
            // If the current test item belongs to the stable flow...
            else {
                // Get the XY coordinates for a given stimulus number from the stable set file
                $xy = loadTriangle($cond, $chain, ($gen-1), "s", $stimulus_number);
            }

            // If the participant is in condition 1
            if ($cond == 1) {
                // Output JavaScript to check that the participant has not given a blank answer
                echo "function CheckAnswer() { if (document.f.a.value == '') { return false; } return true; }\n\n";
            }
            // If the participant is in condition 2, we want some JavaScript to enforce expressivity
            else {
                // Get the words that the participant has used so far
                $words = getWords($cond, $chain, $gen, $stimulus_set);
                // Implode the array of words into a string
                $used_words = "\"". implode("\", \"", $words) ."\"";
                
                // Output JavaScript to check that the participant's answer is not a duplicate
                echo "function CheckAnswer() { if (document.f.a.value == '') {return false;} var used_words = [". $used_words ."]; if (used_words.indexOf(document.f.a.value) != -1) { document.message.duplicate.value = 'Ooops! You already used this word to describe another triangle. Please use a different word for this one.'; document.f.a.value = ''; return false; } return true; }\n\n";
            }
        }
        // Output JavaScript to draw the triangle on the canvas
        echo "function DrawTriangle() { var canvas = document.getElementById('rectangle'); var c = canvas.getContext('2d'); c.beginPath(); c.moveTo(". $xy[0] .", ". $xy[3] ."); c.lineTo(". $xy[1] .", ". $xy[4] ."); c.lineTo(". $xy[2] .", ". $xy[5] ."); c.closePath(); c.lineWidth=". $triangle_line_thickness ."; c.stroke(); c.beginPath(); c.arc(". $xy[0] .", ". $xy[3] .", ". $orienting_spot_radius .", 0, 2 * Math.PI, false); c.fill(); c.lineWidth = 1; c.strokeStyle = 'black'; c.stroke(); }\n";
    }
?>
</script>
        
</head>

<body<?php
    // If the current page is a training or test page, load the relevant JavaScript
    if ($page == "experiment" AND $map_position[0] == "TS") { echo " onload='TestingLoad()'"; }
    elseif ($page == "experiment" AND $map_position[0] == "TR") { echo " onload='TrainingLoad()'"; }
?>>

<table style='width:100%; height:750px;'>
<tr>
<td style='text-align:center;'>
<?php

/////////////////////////////////////////////////////////////////////////////////////////////////////////
// Parameters page

    if ($page == "parameters") {
        echo "<p class='page head'>Settings</p><hr style='height:1; width:580px;' /><form id='parameters' name='f' method='post' action='index.php'><input name='page' type='hidden' value='validation' /><table style='width:400px; margin-left:auto; margin-right:auto;'><tr><td style='width:190px; text-align:right;'><span class='page body'>Diffusion chain:</span></td><td style='width:20px;'></td><td style='width:190px;'><input name='chain' type='text' id='chain' autocomplete='off' style='font:Helvetica Neue; font-size:20px' size='8' /></td></tr><tr><td style='width:190px;'></td><td style='width:20px;'></td><td style='width:190px;'></td></tr><tr><td style='width:190px; text-align:right;'><span class='page body'>Generation:</span></td><td style='width:20px;'></td><td style='width:190px;'><input name='gen' type='text' id='generation' autocomplete='off' style='font:Helvetica Neue; font-size:20px' size='8' /></td></tr><tr><td style='width:190px;'></td><td style='width:20px;'></td><td style='width:190px;'></td></tr><tr><td style='width:190px; text-align:right;'><span class='page body'>Condition:</span></td><td style='width:20px;'></td><td style='width:190px;'><span class='page body'><input name='condition' type='radio' value='1' checked /> Experiment 1<br /><input name='condition' type='radio' value='2' /> Experiment 2</span></td></tr></table><hr style='height:1; width:580px;' /><p><input type='submit' name='submit' value='Okay' style='font-family:Helvetica Neue; font-size:30px;' /></p></form>";
    }

/////////////////////////////////////////////////////////////////////////////////////////////////////////
// Validation page
        
    elseif ($page == "validation") {
        
        // A function to output a row on the validation page
        function validationTableRow($colour, $message) {
            return "<tr><td style='width:30px;'><img src='images/". $colour .".png' width='16' height='16' alt='light' /></td><td style='width:550px; text-align:left;'><p class='regular'>". $message ."</p></td></tr>";
        }
        
        echo "<p class='page head'>Validation</p><table style='margin-left:auto; margin-right:auto;'><tr><td colspan='2'><hr style='height:1; width:580px;' /></td></tr>";

        // Check that the chain code is valid
        if (checkChain($_POST["chain"]) == True) { echo validationTableRow("green", "Chain " . $_POST["chain"]); }
        else { echo validationTableRow("red", "Chain \"". $_POST["chain"] ."\" is invalid"); $error_count ++; }

        // Check that the generation number is valid
        if (checkGen($_POST["gen"]) == True) { echo validationTableRow("green", "Generation " . $_POST["gen"]); }
        else { echo validationTableRow("red", "Generation \"". $_POST["gen"] ."\" is invalid"); $error_count ++; }

        // Check the condition number is valid
        if ($_POST["condition"] == 1 OR $_POST["condition"] == 2) { echo validationTableRow("green", "Experimental condition " . $_POST["condition"]); }
        else { echo validationTableRow("red", "Condition \"". $_POST["condition"] ."\" is invalid"); $error_count ++; }

        // Check that there are $set_size words in the input set
        if (checkInputSet($_POST["condition"], $_POST["chain"], $_POST["gen"]) == True) { echo validationTableRow("green", "Words in the input set are valid"); }
        else { echo validationTableRow("red", "Input set file does not contain $set_size words"); $error_count ++; }
        
        // Check that the data files exist for writing
        if (checkDataFilesExist($_POST["condition"], $_POST["chain"], $_POST["gen"]) == True) { echo validationTableRow("green", "Output data files are ready for writing"); }
        else { echo validationTableRow("red", "Missing output data files at /data/" . $_POST["condition"] . "/" . $_POST["chain"] . "/"); $error_count ++; }

        // Check that sound files exist for the words in the input set
        $words = getWords($_POST["condition"], $_POST["chain"], ($_POST["gen"]-1), "d");
        $missing_words = checkSoundFiles($words);
        if (count($missing_words) == 0) { echo validationTableRow("green", "Required sound files are available"); }
        else {
            // If there are missing words, output a list of them
            for ($i=0; $i < count($missing_words); $i++) {
                $missing_words_list = $missing_words_list . $missing_words[$i] . ", ";
            }
            echo validationTableRow("red", "The following sound files are missing: " . substr($missing_words_list, 0, -2));
            $error_count ++;
        }
        
        // If the above validation functions produce no errors, display messages to check the volume level and keyboard layout
        if ($error_count == 0) {
            // Sound warning
            echo validationTableRow("orange", "Is the volume level okay?");
        
            // Keyboard layout warning
            echo validationTableRow("orange", "Are you using the Alpha-only keyboard layout?");
        }
        
        echo "<tr><td colspan='2'><hr style='height:1; width:580px;' /></td></tr></table><form id='parameters' name='f' method='post' action='index.php'><input name='page' type='hidden' value='experiment' /><input name='chain' type='hidden' value='". $_POST["chain"] ."' /><input name='cond' type='hidden' value='". $_POST["condition"] ."' /><input name='gen' type='hidden' value='". $_POST["gen"] ."' />";
        
        // If the above validation functions produce no errors, display the "Begin experiment" button and embed the sound check file
        if ($error_count == 0) {
            echo "<p><input type='submit' name='submit' value='Begin experiment' style='font-family:Helvetica Neue; font-size:30px;' /></p></form><audio id='alex' src='sound_check.m4a' preload='auto' autoplay></audio>";
        }
    }
        
/////////////////////////////////////////////////////////////////////////////////////////////////////////
// Experiment pages
        
    elseif ($page == "experiment") {
        
        // Welcome page         -------------------------------------------------------------------------
        if ($map_position[0] == "BEGIN") {
            
            // Clear the data files in case they already contain content
            clearFiles($cond, $chain, $gen);
            
            // Write the condition, chain, and generation number to the detect file for use by the status tracker
            writeFile("detect", $cond . "||" . $chain . "||" . $gen);
            
            // Output HTML for the welcome page
            echo "<p class='large'>Stage 1: Training</p><p>&nbsp;</p><p class='regular'>You will see a selection of triangles along with their names. After a few<br />seconds the name will disappear. Type the name back in<br />and press enter to move onto the next one.</p><p class='regular'> Try to learn the word for each triangle as best as you can.</p><p>&nbsp;</p><p class='medium'>Press the enter key when you’re ready to begin training</p><script type='text/Javascript'>document.onkeypress = KeyCheck;</script>";
        }
        
        // Training page         -------------------------------------------------------------------------
        elseif ($map_position[0] == "TR") {
            
            // Output HTML for the training page
            echo "<audio id='alex' src='vocalizations/". $training_word .".m4a' preload='auto'></audio><table style='width:800px; margin-left:auto; margin-right:auto;'><tr><td><canvas id='rectangle' width='". $canvas_width ."' height='". $canvas_height ."' style='border:gray 1px dashed'></canvas></td></tr><tr><td><form id='testing' name='f' method='post' action='index.php' onsubmit='return CheckWordMatch()'><p class='large'><input name='a' type='text' value='' id='testtext' autocomplete='off' style='border:hidden; font-family:Helvetica Neue; font-size:40px; font-weight:lighter; text-align:center; outline:none' size='60' /></p><img id='feedback' src='images/spacer.gif' width='50' height='50' alt='feedback' /></form></td></tr></table>";
        }
        
        // Testing page         -------------------------------------------------------------------------
        elseif ($map_position[0] == "TS") {
            
            // If this is not the first test item (indicated by the fact that $current is set to nothing), do the following...
            if ($_POST["current"] != "") {
                // Create an XY array from the previous XY coordinates
                $last_xy = array($_POST["last_x1"], $_POST["last_x2"], $_POST["last_x3"], $_POST["last_y1"], $_POST["last_y2"], $_POST["last_y3"]);
                
                // Save the previous answer to the relevant file
                saveAnswer($cond, $chain, $gen, $_POST["current"], $_POST["a"], $last_xy);
            }
            
            // Output HTML for the test page
            echo "<table style='width:800px; margin-left:auto; margin-right:auto;'><tr><td><canvas id='rectangle' width='". $canvas_width ."' height='". $canvas_height ."' style='border:gray 1px dashed'></canvas></td></tr><tr><td><form id='testing' name='f' method='post' action='index.php' onsubmit='return CheckAnswer()'><input name='page' type='hidden' value='experiment' /><input name='map' type='hidden' value='". $new_map ."' /><input name='chain' type='hidden' value='". $chain ."' /><input name='cond' type='hidden' value='". $cond ."' /><input name='gen' type='hidden' value='". $gen ."' /><input name='current' type='hidden' value='". $map_position[1] ."' /><input name='last_x1' type='hidden' value='". $xy[0] ."' /><input name='last_x2' type='hidden' value='". $xy[1] ."' /><input name='last_x3' type='hidden' value='". $xy[2] ."' /><input name='last_y1' type='hidden' value='". $xy[3] ."' /><input name='last_y2' type='hidden' value='". $xy[4] ."' /><input name='last_y3' type='hidden' value='". $xy[5] ."' /><p class='large'><input name='a' type='text' value='' id='testtext' autocomplete='off' style='border:hidden; font-family:Helvetica Neue; font-size:40px; font-weight:lighter; text-align:center; outline:none' size='60' /></p></form>";
            
            // If participant is in the second condition
            if ($cond == 2) {
                // Output a textbox in which to tell them if they've duplicated a word
                echo "<form id='mess' name='message'><p class='large'><input type='text' name='duplicate' value='' id='dup' style='border:hidden; color:red; font-family:Helvetica Neue; font-size:14px; font-weight:lighter; text-align:center; outline:none;' size='120' /></p></form>";
            }
            
            echo "</td></tr></table>";
        }
        
        // Break page         -------------------------------------------------------------------------
        elseif ($map_position[0] == "BREAK") {
            
            // Output HTML for the break page
            echo "<p class='large'>Stage 2: Testing</p><p class='medium'>The test will automatically begin in one minute</p><p>&nbsp;</p><table style='margin-left:auto; margin-right:auto;'><tr><td><script type='application/javascript'>var myCountdown2 = new Countdown({style: \"flip\", time: 60, width:100, height:80, rangeHi:'second', onComplete: NextPage, labels: {color: \"#FFFFFF\"}});</script></td></tr></table><p>&nbsp;</p><p class='regular'>You will see a selection of triangles one at a time. This time you will not be given the name.<br />Instead you must type in what you think the name is based on the training you have just<br />completed. After you've typed in the name, press enter to move on to the next one.</p><p class='regular'>You may find it very difficult to remember the words for different triangles.<br />Simply go with your instinct and type in a name that feels right.</p>";
            
            // If the participant is in the second condition...
            if ($_GET["cond"] == 2) {
                // Add a reminder to say that they can't use the same word more than once
                echo "<p class='regular'>Remember: you can't use the same word more than once.</p>";
            }
        }
        
        // End page         -------------------------------------------------------------------------
        elseif ($map_position[0] == "END") {
            
            // Create an XY array from the previous XY coordinates
            $last_xy = array($_POST["last_x1"], $_POST["last_x2"], $_POST["last_x3"], $_POST["last_y1"], $_POST["last_y2"], $_POST["last_y3"]);
            
            // Save the final answer (and sort the stable data file back to its unshuffled order)
            saveFinalAnswer($cond, $chain, $gen, $_POST["current"], $_POST["a"], $last_xy);
            
            // Output HTML for the completion page
            echo "<p class='large'>Experiment complete</p><p class='medium'>Thanks for your participation</p><p>&nbsp;</p><img src='images/smile.png' width='145' alt='flatlander smile' />";
        }
        
        // Return error, if the requested experiment page is invalid
        else {
            echo "<h1>Map error</h1><p>Please inform the experiment supervisor.</p>";
        }
    }
        
/////////////////////////////////////////////////////////////////////////////////////////////////////////
// Return error, if the requested page is invalid
        
    else {
        echo "<h1>Page error</h1><p>Please inform the experiment supervisor.</p>";
    }
        
/////////////////////////////////////////////////////////////////////////////////////////////////////////

?>

</td>
</tr>
</table>
</body>
</html>
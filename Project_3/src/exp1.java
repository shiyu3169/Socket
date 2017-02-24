import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Created by Ben_Big on 2/23/17.
 */


/*
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class RunShellCommandFromJava {

    public static void main(String[] args) {

        String command = "ping -c 3 www.google.com";

        Process proc = Runtime.getRuntime().exec(command);

        // Read the output

        BufferedReader reader =
              new BufferedReader(new InputStreamReader(proc.getInputStream()));

        String line = "";
        while((line = reader.readLine()) != null) {
            System.out.print(line + "\n");
        }

        proc.waitFor();

    }
}
 */

public class exp1 {

    public static boolean findLinesOfInterest(String line){
        Pattern pattern = Pattern.compile("^d .* tcp" +   //Dropped Packet
                "|^r (?:\\S+ ){2}(?<to>\\S+) (?:tcp|ack) (?:\\S+ ){4}(\\k<to>)\\." +   //Packet arrives at destination
                "|^\\- .*? (?<from>\\S+) \\d+ tcp .*? (\\k<from>)\\."); //Packet is sent out from a router
        Matcher m = pattern.matcher(line);
        return m.find();
    }


    public static void runTCLFile(String command){
        String line="";
        try{
            Process proc=Runtime.getRuntime().exec(command);
            BufferedReader reader=new BufferedReader(new InputStreamReader(proc.getInputStream()));
            lineObjectAnalyzer analyzer=new lineObjectAnalyzer();

            while ((line = reader.readLine()) != null) {
                if (findLinesOfInterest(line)){
                    //System.out.println(line);
                    lineObject newLine=new lineObject(line);
                    analyzer.processNewLine(newLine);
                }

            }

            System.out.println(analyzer.getAverageRTT());
            System.out.println(analyzer.getDropRate());
            System.out.println(analyzer.getThroughput());

        }catch (IOException e){
            System.out.println(e);
        }
    }

    public static void main(String[] args){

        runTCLFile("ns exp.tcl TCP 10mb");

        /*
        String test1="r 5.5556 1 2 tcp 1040 ------- 1 0.0 2.0 1100 5601";
        String test2="- 5.558032 2 3 tcp 1040 ------- 1 0.0 2.0 1101 5603";
        String test3="- 5.558032 2 3 tcp 1040 ------- 1 0.0 250 1101 5603";
        System.out.println(findLinesOfInterest(test1));
        System.out.println(findLinesOfInterest(test2));
        System.out.println(findLinesOfInterest(test3));
        */








    }




}

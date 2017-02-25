import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Created by Ben_Big on 2/23/17.
 */



public class exp1 {

    public static boolean findLinesOfInterest(String line){
        Pattern pattern = Pattern.compile("^d .* tcp" +   //Dropped Packet
                "|^r (?:\\S+ ){2}(?<to>\\S+) (?:tcp|ack) (?:\\S+ ){4}(\\k<to>)\\." +   //Packet arrives at destination
                "|^\\- .*? (?<from>\\S+) \\d+ tcp .*? (\\k<from>)\\."); //Packet is sent out from a router
        Matcher m = pattern.matcher(line);
        return m.find();
    }


    public static void runTCLFile(String command, int CBRRate, expOneDataPointsCollector collector){
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
            collector.addDropRate(CBRRate,analyzer.getDropRate());
            collector.addThroughput(CBRRate,analyzer.getThroughput());
            collector.addRTT(CBRRate,analyzer.getAverageRTT());
            /*
            System.out.println(analyzer.getAverageRTT());
            System.out.println(analyzer.getDropRate());
            System.out.println(analyzer.getThroughput());*/

        }catch (IOException e){
            System.out.println(e);
        }
    }

    public static void main(String[] args){

        expOneDataPointsCollector collector=new expOneDataPointsCollector();

        int initialCBRRate=0;
        int interval=1;


        for (int rate=initialCBRRate;rate<=10;rate+=interval) {
            String command="ns exp0.tcl TCP "+rate+"mb";
            runTCLFile(command, rate, collector);
        }
        System.out.println(collector.toString());

    }
}

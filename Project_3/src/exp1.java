import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Created by Ben_Big on 2/23/17.
 */



public class exp1 {


    public static void runTCLFile(String command, int CBRRate, expOneDataPointsCollector collector){
        String line="";
        try{
            Process proc=Runtime.getRuntime().exec(command);
            BufferedReader reader=new BufferedReader(new InputStreamReader(proc.getInputStream()));
            lineObjectAnalyzer analyzer=new lineObjectAnalyzer();

            while ((line = reader.readLine()) != null) {
                if (lineObjectAnalyzer.findLinesOfInterest(line)){
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

        int initialCBRRate=1;
        int interval=1;

        String TCPFlavor = "";

        if (args.length==1){
            TCPFlavor = args[0];
        }


        for (int rate=initialCBRRate;rate<=10;rate+=interval) {
            String command="/course/cs4700f12/ns-allinone-2.35/bin/ns exp.tcl "+TCPFlavor+" "+rate+"mb";
            runTCLFile(command, rate, collector);
        }
        System.out.println(collector.toString());

    }
}

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

/**
 * Created by Ben_Big on 2/24/17.
 */
public class exp2 {
    public static void runTCLFile(String command, int CBRRate, expTwoDataPointsCollector collector){
        String line="";
        try{
            Process proc=Runtime.getRuntime().exec(command);
            BufferedReader reader=new BufferedReader(new InputStreamReader(proc.getInputStream()));
            lineObjectAnalyzer analyzerOne=new lineObjectAnalyzer();
            lineObjectAnalyzer analyzerTwo=new lineObjectAnalyzer();

            while ((line = reader.readLine()) != null) {
                if (lineObjectAnalyzer.findLinesOfInterest(line)){
                    //System.out.println(line);
                    lineObject newLine=new lineObject(line);
                    if (newLine.flow==1){
                        analyzerOne.processNewLine(newLine);
                    }
                    else if (newLine.flow==3){
                        analyzerTwo.processNewLine(newLine);
                    }
                }
            }


            collector.addDropRate(CBRRate,analyzerOne.getDropRate(),1);
            collector.addThroughput(CBRRate,analyzerOne.getThroughput(),1);
            collector.addRTT(CBRRate,analyzerOne.getAverageRTT(),1);


            collector.addDropRate(CBRRate,analyzerOne.getDropRate(),2);
            collector.addThroughput(CBRRate,analyzerOne.getThroughput(),2);
            collector.addRTT(CBRRate,analyzerOne.getAverageRTT(),2);


            /*
            System.out.println(analyzerOne.getAverageRTT());
            System.out.println(analyzerOne.getDropRate());
            System.out.println(analyzerOne.getThroughput());*/

        }catch (IOException e){
            System.out.println(e);
        }
    }


    public static void main(String[] args) {

        expTwoDataPointsCollector collector = new expTwoDataPointsCollector();

        int initialCBRRate = 1;
        int interval = 1;


        for (int rate = initialCBRRate; rate <= 10; rate += interval) {
            String command = "ns exp.tcl TCP " + rate + "mb";
            runTCLFile(command, rate, collector);
        }
        System.out.println(collector.toString());

    }
}

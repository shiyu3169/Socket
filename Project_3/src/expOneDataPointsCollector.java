import java.util.HashMap;

/**
 * Created by Ben_Big on 2/23/17.
 */
public class expOneDataPointsCollector {

    private HashMap<Integer, Float> CBRrateToDropRate=new HashMap<>();
    private HashMap<Integer, Double> CBRrateToThroughput=new HashMap<>();
    private HashMap<Integer, Float> CBRrateToRTT=new HashMap<>();

    public void addDropRate(int rate, float dropRate){
        if (!CBRrateToDropRate.containsKey(rate)) {
            CBRrateToDropRate.put(rate, dropRate);
        }
    }

    public void addThroughput(int rate, double throughput){
        if (!CBRrateToThroughput.containsKey(rate)) {
            CBRrateToThroughput.put(rate, throughput);
        }
    }

    public void addRTT(int rate,float rtt){
        if (!CBRrateToRTT.containsKey(rate)) {
            CBRrateToRTT.put(rate, rtt);
        }
    }

    @Override
    public String toString(){
        return "Droprate: "+CBRrateToDropRate.toString()+"\n"+
                "Throughput: "+CBRrateToThroughput.toString()+"\n"+
                "RTT: "+CBRrateToRTT.toString();
    }



}

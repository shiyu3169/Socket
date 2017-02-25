import java.util.HashMap;

/**
 * Created by Ben_Big on 2/24/17.
 */
public class expTwoDataPointsCollector {

    private HashMap<Integer, Float>[] CBRrateToDropRate=new HashMap[2];
    private HashMap<Integer, Double>[] CBRrateToThroughput=new HashMap[2];
    private HashMap<Integer, Float>[] CBRrateToRTT=new HashMap[2];

    public expTwoDataPointsCollector(){
        CBRrateToDropRate[0]=new HashMap<>();
        CBRrateToDropRate[1]=new HashMap<>();
        CBRrateToThroughput[0]=new HashMap<>();
        CBRrateToThroughput[1]=new HashMap<>();
        CBRrateToRTT[0]=new HashMap<>();
        CBRrateToRTT[1]=new HashMap<>();
    }



    public void addDropRate(int rate, float dropRate, int index){
        if (!CBRrateToDropRate[index-1].containsKey(rate)) {
            CBRrateToDropRate[index-1].put(rate, dropRate);
        }
    }

    public void addThroughput(int rate, double throughput, int index){
        if (!CBRrateToThroughput[index-1].containsKey(rate)) {
            CBRrateToThroughput[index-1].put(rate, throughput);
        }
    }

    public void addRTT(int rate,float rtt, int index){
        if (!CBRrateToRTT[index-1].containsKey(rate)) {
            CBRrateToRTT[index-1].put(rate, rtt);
        }
    }

    @Override
    public String toString(){
        return  "flow 1: \n"+
                "1 Droprate: "+CBRrateToDropRate[0].toString()+"\n"+
                "1 Throughput: "+CBRrateToThroughput[0].toString()+"\n"+
                "1 RTT: "+CBRrateToRTT[0].toString()+"\n"+
                "flow 2: \n"+
                "2 Droprate: "+CBRrateToDropRate[1].toString()+"\n"+
                "2 Throughput: "+CBRrateToThroughput[1].toString()+"\n"+
                "2 RTT: "+CBRrateToRTT[1].toString()+"\n";
    }




}

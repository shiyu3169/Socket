import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Created by Ben_Big on 2/25/17.
 */
public class expThreeDataPointsCollector {


    public  HashMap<Double, List<Float>> timeToResult=new HashMap<>();
    private double TCPStartTime=1;

    public void addResult(double time, List<Float> result){
        if (time<=TCPStartTime) return;
        if (!timeToResult.containsKey(time)) {
            timeToResult.put(time, result);
        }
    }


    @Override
    public String toString(){
        String str="";
        /*
        for (Map.Entry<Double, List<Float>> entry : timeToResult.entrySet()){
               double time=entry.getKey();
               List<Float> result=entry.getValue();
               str+="time: "+time+" "+"droprate: "+result.get(0)+"\n";
        }*/



        return timeToResult.toString();
    }


}

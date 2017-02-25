import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Created by Ben_Big on 2/23/17.
 */
public class lineObject {

  //  private final static Pattern pattern=Pattern.compile("([\\-rd]) (\\d+\\.\\d+|\\d+) (\\d+) (\\d+) (tcp|ack) (\\d+) .{7} (\\d+) (\\d+)\\.\\d+ (\\d+)\\.\\d+ (\\d+) (\\d+)");
    private final static Pattern pattern=Pattern.compile("([\\-rd]) (\\d+\\.\\d+|\\d+) (\\d+) (\\d+) (tcp|ack) (\\d+) .{7} (\\d+) (\\d+)\\.\\d+ (\\d+)\\.\\d+ (\\d+) (\\d+)");


    protected String event;
    protected float time;
    protected int frm;
    protected int to;
    protected String type;
    protected int size;
    protected int flow;
    protected int src;
    protected int dest;
    protected int seq;
    protected int id;

    public lineObject(String line){
        Matcher matcher=pattern.matcher(line);
        if (matcher.find()) {
            event = matcher.group(1);
            time = Float.parseFloat(matcher.group(2));
            frm = Integer.parseInt(matcher.group(3));
            to = Integer.parseInt(matcher.group(4));
            type = matcher.group(5);
            size=Integer.parseInt(matcher.group(6));
            flow=Integer.parseInt(matcher.group(7));
            src=Integer.parseInt(matcher.group(8));
            dest=Integer.parseInt(matcher.group(9));
            seq=Integer.parseInt(matcher.group(10));
            id=Integer.parseInt(matcher.group(11));
        }


    }
    public static void main(String[] args){

       // String testLine="r 5.5556 1 2 tcp 1040 ------- 1 0.0 2.0 1100 5601";
        String testLine="r 5.5556 1 2 tcp 1040 ------- 1 0.0 2.0 1100 5601";
        lineObject test1=new lineObject(testLine);
        /*
        System.out.println(test1.event);
        System.out.println(test1.time);
        System.out.println(test1.frm);
        System.out.println(test1.to);
        System.out.println(test1.type);
        System.out.println(test1.size);
        System.out.println(test1.flow);
        System.out.println(test1.src);
        System.out.println(test1.dest);
        System.out.println(test1.seq);
        System.out.println(test1.id);*/
    }
}

// ����Ʈ ����Ʈ
using UnityEngine;
using UnityEngine.UI;
using TMPro;


//��� ����Ʈ
using System.Collections;
using UnityEngine.Networking;
using System.Text;
using System.IO;

public class ButtonClick : MonoBehaviour
{


    private string apiUrl_chat = "http://192.168.0.20:8001/chatbot/test_text";
    private string apiUrl = "http://192.168.0.20:8001/chatbot/test_image"; // FastAPI ������ ��������Ʈ URL�� �Է��ϼ���.
/*    private string apiUrl_chat = "http://127.0.0.1:8000/chatbot/test_text";
    private string apiUrl = "http://127.0.0.1:8000/chatbot/test_image"; // FastAPI ������ ��������Ʈ URL�� �Է��ϼ���.*/




    public Button yourButton;
    public TMP_InputField yourInputField;
    public TMP_InputField max_yourInputField;

    public Button yourButton2;
    public RawImage yourRawImage;

    void Start()
    {
        Button btn = yourButton.GetComponent<Button>();
        btn.onClick.AddListener(TaskOnClick);

        Button btn2 = yourButton2.GetComponent<Button>();
        btn2.onClick.AddListener(TaskOnClick2);

    }

    void TaskOnClick()
    {
        string inputText = yourInputField.text;
        Debug.Log(inputText);
        string json = "{\"text\":\""+ inputText + "\"}";

        // JSON �����͸� ����Ʈ �迭�� ��ȯ
        byte[] jsonData = Encoding.UTF8.GetBytes(json);
        Debug.Log("�����ͺ�����");
        StartCoroutine(PostJson(jsonData));
    }





    void TaskOnClick2()
    {
        string json = "{\"text\":\"Image Test Hi!\"}";

        // JSON �����͸� ����Ʈ �迭�� ��ȯ
        byte[] jsonData = Encoding.UTF8.GetBytes(json);


        StartCoroutine(PostImageFile(jsonData));


        Texture2D[] textures = Resources.LoadAll<Texture2D>("Images");

        // �̹��� �߿��� �������� �ϳ��� �����մϴ�.
        Texture2D randomTexture = textures[Random.Range(0, textures.Length)];

        // ������ �̹����� Raw Image�� �ؽ�ó�� �����մϴ�.
        yourRawImage.texture = randomTexture;

    }

    IEnumerator PostImageFile(byte[] jsonData)
    {
        using (UnityWebRequest www = new UnityWebRequest(apiUrl, "POST"))
        {
            www.uploadHandler = new UploadHandlerRaw(jsonData);
            www.downloadHandler = new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();

            void SaveImage(byte[] imageBytes, string fileName)
            {
                File.WriteAllBytes(fileName, imageBytes);
                Debug.Log("Image saved");
            }

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError(www.error);
            }
            else
            {

                SaveImage(www.downloadHandler.data, "./Assets/Resources/Images/test.jpg");
                Debug.Log("Success!!!!!");


                // ���⿡�� responseText�� �Ľ��Ͽ� ������� ����
            }
        }
    }

    IEnumerator PostJson(byte[] jsonData)
    {
        using (UnityWebRequest www = new UnityWebRequest(apiUrl_chat, "POST"))
        {
            www.uploadHandler = new UploadHandlerRaw(jsonData);
            www.downloadHandler = new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError(www.error);
            }
            else
            {
                string responseText = www.downloadHandler.text;
                Debug.Log("Response from server: " + responseText);
                max_yourInputField.text=responseText;
                // ���⿡�� responseText�� �Ľ��Ͽ� ������� ����
            }
        }
    }


}
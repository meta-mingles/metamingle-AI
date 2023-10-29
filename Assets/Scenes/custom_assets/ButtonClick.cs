// 디폴트 임포트
using UnityEngine;
using UnityEngine.UI;
using TMPro;


//통신 임포트
using System.Collections;
using UnityEngine.Networking;
using System.Text;
using System.IO;

public class ButtonClick : MonoBehaviour
{


    private string apiUrl_chat = "http://192.168.0.20:8001/chatbot/test_text";
    private string apiUrl = "http://192.168.0.20:8001/chatbot/test_image"; // FastAPI 서버의 엔드포인트 URL을 입력하세요.
/*    private string apiUrl_chat = "http://127.0.0.1:8000/chatbot/test_text";
    private string apiUrl = "http://127.0.0.1:8000/chatbot/test_image"; // FastAPI 서버의 엔드포인트 URL을 입력하세요.*/




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

        // JSON 데이터를 바이트 배열로 변환
        byte[] jsonData = Encoding.UTF8.GetBytes(json);
        Debug.Log("데이터보내기");
        StartCoroutine(PostJson(jsonData));
    }





    void TaskOnClick2()
    {
        string json = "{\"text\":\"Image Test Hi!\"}";

        // JSON 데이터를 바이트 배열로 변환
        byte[] jsonData = Encoding.UTF8.GetBytes(json);


        StartCoroutine(PostImageFile(jsonData));


        Texture2D[] textures = Resources.LoadAll<Texture2D>("Images");

        // 이미지 중에서 랜덤으로 하나를 선택합니다.
        Texture2D randomTexture = textures[Random.Range(0, textures.Length)];

        // 선택한 이미지를 Raw Image의 텍스처로 설정합니다.
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


                // 여기에서 responseText를 파싱하여 결과값을 추출
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
                // 여기에서 responseText를 파싱하여 결과값을 추출
            }
        }
    }


}